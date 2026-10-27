#!/usr/bin/env python3
"""Respaldo del kit hefesto-archivo (Paperless-ngx + Supabase/Postgres + Valkey).

El .env nunca se copia en claro: al respaldo solo van sus nombres (env.vars) y,
si hay receptor age, el .env cifrado (env.age). Ver docs/CONTRATO-RESPALDO.md.
"""
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (escribir_manifiesto, ejecutar, exportar_env,
                               marcar_fallido)

SOFTWARE = "hefesto-archivo"
VERSION = "3.3.1"
DATABASE = "postgresql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)
TARIFS = ["data", "media", "consume", "export"]


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    if not (RAIZ / ".env").is_file():
        raise SystemExit("Falta .env")
    for svc in ["app", "broker"]:
        if not dc("ps", "--status", "running", "-q", svc, capture_output=True, text=True).stdout.strip():
            raise SystemExit("app/broker no activos en este contexto")
    carpeta = RAIZ / "backups" / datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    carpeta.mkdir(parents=True, mode=0o700)
    try:
        dc("stop", "-t", "120", "app")
        with (carpeta / "public.dump").open("wb") as out:
            dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "pg_dump", "dbtools",
               "--format=custom", "--schema=public", "--no-owner", "--no-acl", stdout=out)
        dc("exec", "-T", "broker", "sh", "-c", 'VALKEYCLI_AUTH="$BROKER_PASSWORD" valkey-cli SAVE')
        dc("stop", "broker")
        for nombre in TARIFS:
            with (carpeta / (nombre + ".tar.gz")).open("wb") as out:
                dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar", "app",
                   "-czf", "-", "-C", "/usr/src/paperless/" + nombre, ".", stdout=out)
        with (carpeta / "broker.tar.gz").open("wb") as out:
            dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar", "broker",
               "-czf", "-", "-C", "/data", ".", stdout=out)
        shutil.copy2(RAIZ / "compose.yaml", carpeta / "compose.yaml")
        meta = exportar_env(RAIZ, carpeta)
        artefactos = ["public.dump", "broker.tar.gz", "env.vars", "compose.yaml"]
        artefactos += [n + ".tar.gz" for n in TARIFS]
        if (carpeta / "env.age").is_file():
            artefactos.append("env.age")
        escribir_manifiesto(carpeta, SOFTWARE, VERSION, DATABASE, artefactos, extra=meta)
    except Exception:
        marcar_fallido(carpeta, SOFTWARE, VERSION, DATABASE)
        raise
    finally:
        dc("start", "broker")
        dc("start", "app")
    print("Respaldo completo:", carpeta)
    print("El .env no viaja en claro: solo env.vars y, si hay receptor age, env.age.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
