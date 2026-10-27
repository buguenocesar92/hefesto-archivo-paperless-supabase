#!/usr/bin/env python3
"""Restaura solo el esquema public de Paperless en un proyecto nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Valida manifiesto y sha256 antes de tocar el destino, exige el esquema
public vacio y deja restore-report.json y auditoria.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (RespaldoError, auditar, ejecutar, ejecutar_check,
                               escribir_informe, opciones_restore)

SOFTWARE = "hefesto-archivo"
VERSION = "3.3.1"
DATABASE = "postgresql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    origen = Path(origen).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE)
    dump = origen / "public.dump"
    if modo == "dry-run":
        print("Simulacion: el respaldo es integro y no se escribio nada.")
        print("Para restaurar de verdad: --confirmar CONFIRMAR_RESTAURACION")
        return 0
    if dc("ps", "--status", "running", "-q", "app", capture_output=True, text=True).stdout.strip():
        raise RespaldoError("Detener Paperless antes de restaurar en un destino nuevo", 5)
    count = dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "psql", "dbtools", "-Atc",
               "SELECT count(*) FROM pg_tables WHERE schemaname='public'",
               capture_output=True, text=True).stdout.strip()
    if count != "0":
        raise RespaldoError("El esquema public del destino no esta vacio; no se sobrescriben datos", 5)
    with dump.open("rb") as flujo:
        toc = dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "pg_restore", "dbtools",
                 "--list", stdin=flujo, stdout=subprocess.PIPE).stdout.decode()
    # public ya existe en Supabase: no se dropea ni se restaura su entrada SCHEMA.
    lineas = [l for l in toc.splitlines() if not re.match(r"^\d+;\s+\d+\s+\d+\s+SCHEMA\s+-\s+public(?:\s|$)", l)]
    with tempfile.TemporaryDirectory(prefix="hefesto-restore-") as d:
        ruta = Path(d) / "restore.list"
        ruta.write_text("\n".join(lineas) + "\n")
        os.chmod(d, 0o755)
        os.chmod(ruta, 0o644)
        with dump.open("rb") as flujo:
            dc("run", "--rm", "--no-deps", "-T", "-v", d + ":/restore:ro", "--entrypoint",
               "pg_restore", "dbtools", "--exit-on-error", "--no-owner", "--no-acl",
               "--use-list=/restore/restore.list", "--dbname=postgres", stdin=flujo)
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="esquema_restaurado", destino=str(RAIZ))
    auditar(RAIZ, operacion="restore_db", kit=SOFTWARE, origen=str(origen),
            destino=str(RAIZ), resultado="esquema_restaurado")
    print("Esquema restaurado. Faltan archivos/broker y pruebas; servicios no iniciados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
