#!/usr/bin/env python3
"""Restaura los archivos de Paperless en un destino nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Valida manifiesto, sha256 y rutas del tar antes de extraer, exige los
volumenes destino vacios y deja restore-report.json y auditoria.
"""
import os
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import (RespaldoError, auditar, ejecutar, ejecutar_check,
                               escribir_informe, opciones_restore)

SOFTWARE = "hefesto-archivo"
VERSION = "3.3.1"
DATABASE = "postgresql"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)
ITEMS = [("data", "app", "/usr/src/paperless/data"),
         ("media", "app", "/usr/src/paperless/media"),
         ("consume", "app", "/usr/src/paperless/consume"),
         ("export", "app", "/usr/src/paperless/export"),
         ("broker", "broker", "/data")]


def dc(*args, **kw):
    return subprocess.run(["docker", "compose", *args], check=True, **kw)


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    origen = Path(origen).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE)
    # Valida cada archivo y cada destino antes de extraer nada.
    for nombre, svc, destino in ITEMS:
        archivo = origen / (nombre + ".tar.gz")
        with tarfile.open(archivo, "r:gz") as archivo_tar:
            for miembro in archivo_tar:
                ruta = PurePosixPath(miembro.name)
                if ruta.is_absolute() or ".." in ruta.parts or not (miembro.isfile() or miembro.isdir()):
                    raise RespaldoError("Ruta o tipo no permitido en " + nombre + ": revisar el respaldo", 2)
    if modo == "dry-run":
        print("Simulacion: el respaldo es integro y no se escribio nada.")
        print("Para restaurar de verdad: --confirmar CONFIRMAR_RESTAURACION")
        return 0
    for svc in ["app", "broker"]:
        if dc("ps", "--status", "running", "-q", svc, capture_output=True, text=True).stdout.strip():
            raise RespaldoError("Detener app y broker antes de restaurar", 5)
    for nombre, svc, destino in ITEMS:
        ocupado = dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "find", svc, destino,
                     "-mindepth", "1", "-maxdepth", "1", capture_output=True, text=True).stdout.strip()
        if ocupado:
            raise RespaldoError("Volumen no vacio: " + nombre + "; usar destino nuevo", 5)
    for nombre, svc, destino in ITEMS:
        with (origen / (nombre + ".tar.gz")).open("rb") as flujo:
            dc("run", "--rm", "--no-deps", "-T", "--entrypoint", "tar", svc,
               "-xzf", "-", "-C", destino, stdin=flujo)
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="archivos_restaurados", destino=str(RAIZ))
    auditar(RAIZ, operacion="restore_files", kit=SOFTWARE, origen=str(origen),
            destino=str(RAIZ), resultado="archivos_restaurados")
    print("Archivos restaurados; servicios no iniciados. Revisar red y colas antes de arrancar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
