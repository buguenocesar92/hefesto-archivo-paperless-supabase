#!/usr/bin/env python3
import os,datetime,subprocess,hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1];os.chdir(p);os.umask(0o077)
def dc(*args,**kw):return subprocess.run(['docker','compose',*args],check=True,**kw)
if not (p/'.env').is_file():raise SystemExit('Falta .env')
for svc in ['app','broker']:
 if not dc('ps','--status','running','-q',svc,capture_output=True,text=True).stdout.strip():raise SystemExit('app/broker no activos en este contexto')
b=p/'backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');b.mkdir(parents=True)
try:
 dc('stop','-t','120','app')
 with (b/'public.dump').open('wb') as out:
  dc('run','--rm','--no-deps','-T','--entrypoint','pg_dump','dbtools','--format=custom','--schema=public','--no-owner','--no-acl',stdout=out)
 dc('exec','-T','broker','sh','-c','VALKEYCLI_AUTH="$BROKER_PASSWORD" valkey-cli SAVE')
 dc('stop','broker')
 for name in ['data','media','consume','export']:
  with (b/(name+'.tar.gz')).open('wb') as out:
   dc('run','--rm','--no-deps','-T','--entrypoint','tar','app','-czf','-','-C','/usr/src/paperless/'+name,'.',stdout=out)
 with (b/'broker.tar.gz').open('wb') as out:
  dc('run','--rm','--no-deps','-T','--entrypoint','tar','broker','-czf','-','-C','/data','.',stdout=out)
 for name in ['.env','compose.yaml']:(b/name).write_bytes((p/name).read_bytes())
 hashes={}
 for f in b.iterdir():
  with f.open('rb') as stream:hashes[f.name]=hashlib.file_digest(stream,'sha256').hexdigest()
 (b/'manifest.json').write_text(json.dumps({'version':'3.3.1','status':'completed','sha256':hashes},indent=2))
finally:
 dc('start','broker');dc('start','app')
print(f'Respaldo: {b}. Cifrar y copiar fuera del VPS; contiene documentos, datos personales y secretos.')
