#!/usr/bin/env python3
import os,sys,json,hashlib,tarfile,subprocess
from pathlib import Path,PurePosixPath
if len(sys.argv)!=2:raise SystemExit('Uso: python3 scripts/restore_files.py /ruta/respaldo')
b=Path(sys.argv[1]).resolve();p=Path(__file__).resolve().parents[1];os.chdir(p)
m=json.loads((b/'manifest.json').read_text())
if m.get('version')!='3.3.1' or m.get('status')!='completed':raise SystemExit('Manifest invalido')
def dc(*args,**kw):return subprocess.run(['docker','compose',*args],check=True,**kw)
for svc in ['app','broker']:
 if dc('ps','--status','running','-q',svc,capture_output=True,text=True).stdout.strip():raise SystemExit('Detener app y broker antes de restaurar')
items=[(n,'app','/usr/src/paperless/'+n) for n in ['data','media','consume','export']]+[('broker','broker','/data')]
# Validate every archive and every destination before extracting anything.
for name,svc,dest in items:
 file=b/(name+'.tar.gz')
 with file.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 if digest!=m['sha256'][file.name]:raise SystemExit('Checksum incorrecto: '+name)
 with tarfile.open(file,'r:gz') as archive:
  for member in archive:
   path=PurePosixPath(member.name)
   if path.is_absolute() or '..' in path.parts or not(member.isfile() or member.isdir()):raise SystemExit('Ruta/tipo no permitido: revisar respaldo '+name)
 found=dc('run','--rm','--no-deps','-T','--entrypoint','find',svc,dest,'-mindepth','1','-maxdepth','1',capture_output=True,text=True).stdout.strip()
 if found:raise SystemExit('Volumen no vacio: '+name+'; usar destino nuevo')
for name,svc,dest in items:
 with (b/(name+'.tar.gz')).open('rb') as stream:dc('run','--rm','--no-deps','-T','--entrypoint','tar',svc,'-xzf','-','-C',dest,stdin=stream)
print('Archivos restaurados; servicios no iniciados. Revisar red y colas antes de arrancar.')
