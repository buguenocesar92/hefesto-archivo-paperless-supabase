#!/usr/bin/env python3
import os,sys,re,secrets
from pathlib import Path
if len(sys.argv)!=4 or not re.fullmatch(r'[a-z][a-z0-9-]{2,39}',sys.argv[1]) or not re.fullmatch(r'(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}',sys.argv[2]) or not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}',sys.argv[3]):
 raise SystemExit('Uso: python3 scripts/configure.py cliente-demo archivo.tudominio.cl admin@tudominio.cl')
p=Path(__file__).resolve().parents[1];prefix='hefesto-archivo-'+sys.argv[1]
v={'COMPOSE_PROJECT_NAME':prefix,'VOLUME_PREFIX':prefix,'ARCHIVE_HOST':sys.argv[2],'ADMIN_EMAIL':sys.argv[3],'POSTGRES_HOST':'CONFIGURAR','POSTGRES_USERNAME':'paperless_app','SUPABASE_DEDICATED_CONFIRMED':'false','SUPABASE_DATA_API_DISABLED':'false'}
for name in ['POSTGRES_PASSWORD','PAPERLESS_SECRET_KEY','ADMIN_PASSWORD','BROKER_PASSWORD']:v[name]=secrets.token_hex(32)
try:fd=os.open(p/'.env',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:raise SystemExit('.env ya existe; no se modifico')
with os.fdopen(fd,'w') as f:
 for k,value in v.items():f.write(f'{k}={value}\n')
print('.env generado. Configurar Supabase y asignar POSTGRES_PASSWORD al rol; conservar todas las claves.')
