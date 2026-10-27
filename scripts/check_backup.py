#!/usr/bin/env python3
"""Verificacion de integridad de un respaldo de hefesto-archivo.

Codigos de salida: 0 integro, 1 uso, 2 integridad o manifiesto invalido,
4 material sensible en claro dentro del respaldo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo_contrato import ejecutar, ejecutar_check

SOFTWARE = "hefesto-archivo"
VERSION = "3.3.1"
DATABASE = "postgresql"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 scripts/check_backup.py /ruta/respaldo")
    ejecutar_check(sys.argv[1], SOFTWARE, VERSION, DATABASE)
    print("Manifiesto, checksums y ausencia de secretos en claro verificados.")
    print("Esto no demuestra la recuperacion de PostgreSQL ni de Paperless: falta el ensayo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
