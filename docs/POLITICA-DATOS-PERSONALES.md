# Política de tratamiento de datos personales — Archivo documental (Hefesto Studio)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit. Este documento describe qué datos guarda el kit, por qué, cuánto
tiempo los retiene y cómo se exercise los derechos del titular (Ley 21.719).

## 1. Qué datos guarda este kit

El kit de archivo (Paperless-ngx) guarda, por documento archivado:

- **Documento**: PDF, TIFF u Office escaneado, con su texto extraído (OCR) y
  sus metadatos (correspondiente, tipo documental, fecha de creación, etiquetas).
- **Metadatos del documento**: nombre, tamaño, fecha,checksum y la relación con
  su archivo original.
- **Cuentas y permisos**: usuarios de Paperless, sus roles y los permisos por
  etiqueta o por propietario.
- **Cola y estado del procesamiento**: archivos en `consume`, tareas pendientes
  en `export` y el estado de la cola en Valkey.
- **Copias locales de respaldo**: `backups/<timestamp>/` con el dump del esquema
  `public` de PostgreSQL (`public.dump`), los archivos de datos, media, consumo
  y exportación, y la cola del broker.

Los documentos archivados pueden contener datos personales sensibles (identidad,
salud, contratos). El kit es un archivo documental: el tratamiento es el que
defina el cliente que lo opera.

## 2. Qué datos NO guarda este kit

- El `.env` **no** se copia en claro al respaldo: solo sus nombres de
  variable (`env.vars`) y, si hay un receptor `age` configurado, el `.env`
  cifrado (`env.age`). Ver `docs/CONTRATO-RESPALDO.md`, regla 5.
- El kit no envía los documentos a servicios de terceros ni a la nube: el
  procesamiento (OCR,Thunderbird, correos) es local al proyecto.
- El kit no guarda en el respaldo las credenciales del broker en claro: el
  `.env` queda fuera.

## 3. Base legal y deberes

- **Minimización**: el kit guarda el documento y sus metadatos, no datos adicionales de las
  personas. El OCR es local y no se envía a servicios externos.
- **Finalidad**: conservar y consultar documentación del cliente. Los datos no se usan para otros fines ni se ceden a terceros.
- **Seguridad**: los respaldos se cifran en reposo con `age` hacia el destino del operador, la clave privada no está en este servidor y el `.env` nunca sale en claro.
- **Auditoría**: cada respaldo y cada restauración dejan registro en `logs/restore.log` con origen, sha256 verificado, destino y resultado. Es registro de actividades de tratamiento: no guarda valores de secretos.

## 4. Retención

| Dato | Dónde | Retención por defecto | Quién lo borra |
|---|---|---|---|
| Documentos y sus metadatos | PostgreSQL (`public`) + volumen `media` | mientras el cliente los conserve en el archivo | el operador, desde la interfaz |
| Cuentas y permisos | PostgreSQL (`public`) | mientras la cuenta exista | el operador |
| Cola de procesamiento | volumen `consume`, `export` y broker Valkey | mientras haya tareas; el operador la purga | el operador |
| Respaldos en disco | `backups/<timestamp>/` | **a definir por el operador**; el kit no borra nada por su cuenta | el operador |
| Registro de auditoría | `logs/restore.log` | append-only; se trunca por política del cliente | el operador |

**El kit no borra respaldos ni datos por su cuenta.** Borrar es una decisión del
operador, porque un respaldo borrado no se recupera.

## 5. Derechos del titular (acceso, rectificación y supresión)

El cliente que opera el kit debe poder atender las solicitudes de sus
titulares sobre los documentos archivados:

1. **Acceso**: entregar el documento y sus metadatos al titular que lo solicite.
2. **Rectificación**: corregir metadatos o sustituir el archivo desde la interfaz.
3. **Supresión**: eliminar el documento, sus metadatos y los respaldos que lo
   contengan, y dejar constancia en el registro de auditoría.
4. **Revocación del consentimiento**: si el tratamiento depende del
   consentimiento, eliminar el documento archivado.

El kit garantiza que los datos son localizables, corregibles y borrables; el
cliente es quien conoce la identidad de los titulares.

## 6. Verificación

- `bats tests/backup_restore.bats` comprueba, con datos sintéticos, que el
  `.env` no queda en claro, que el manifiesto lleva las cinco claves, que un
  artefacto alterado se rechaza y que un destino no vacío aborta la
  restauración.
- `gitleaks` corre en CI sobre el repositorio y su historial.
