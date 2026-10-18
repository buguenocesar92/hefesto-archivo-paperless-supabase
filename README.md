# Hefesto Archivo · Paperless-ngx3.3.1 + Supabase
Gestión documental con OCR, búsqueda de contenido, remitentes, tipos y etiquetas. Pensado para vender implementación, carga inicial, organización documental, formación y mantenimiento.

## Stack
Imagen oficial Paperless-ngx3.3.1 fijada por digest, PostgreSQL16/17 de Supabase dedicado y broker Valkey9 privado. OCR local en español e inglés (spa+eng). Bases, originales, versiones procesadas, índices, importación/exportación y broker forman parte de la recuperación.

La conexión usa PAPERLESS_DBENGINE=postgresql y PAPERLESS_DB_OPTIONS con TLS verify-full. Se emplean variables de la versión3; no se reutilizan las opciones SSL eliminadas en v3. Supabase almacena metadatos; los documentos permanecen en volúmenes del VPS. No se conectó Supabase Storage/Auth/Realtime.

## Estado real
Paquete revisado estáticamente con documentación de la versión. No se desplegó, ejecutó OCR ni conectó tu Supabase. La aceptación funcional y restauración deben probarse en el VPS. No hay documentos reales ni secretos de terceros incluidos.

## Inicio
1. Crear proyecto Supabase exclusivo y seguir docs/SUPABASE.md.
2. `python3 scripts/configure.py cliente-demo archivo.tudominio.cl admin@tudominio.cl`
3. Asignar al rol paperless_app el POSTGRES_PASSWORD generado; completar host/login y guardar CA como certs/ca.crt.
4. Deshabilitar Data API y confirmar ambas variables de aislamiento.
5. `docker compose -f compose.yaml -f compose.bootstrap.yaml up -d`
6. Túnel desde tu computador: `ssh -L 8000:127.0.0.1:8000 usuario@IP_DEL_VPS`.
7. Abrir http://127.0.0.1:8000; usuario hefesto_admin y ADMIN_PASSWORD de .env. Cambiar contraseña y configurar acceso/MFA nativos según disponibilidad.
8. Seguir docs/COOLIFY.md, cargar documentos ficticios y ejecutar aceptación antes de datos reales.

Docker Compose v2 y Python3.11+ para scripts. Punto inicial orientativo4vCPU/4GB RAM y SSD suficiente para originales+archivados+backups. OCR puede consumir bastante CPU/RAM; este paquete limita a1worker y2threads. Medir tamaños y carga, no prometer documentos ilimitados.

## Alcance y licencia
PDF e imágenes soportadas por procesamiento nativo; no incluye Tika/Gotenberg para documentos Office. No configura proveedores externos de IA, extracción con LLM, correo automático, firma electrónica ni anonimización/redacción. Buscar texto no significa ocultarlo o borrarlo del documento.

Conservar licencia GPL y avisos del proyecto. Hefesto vende servicio/implementación, no exclusividad sobre el software. Este paquete no acredita cumplimiento documental/legal ni autoriza destruir originales físicos.

## Despliegue en Coolify (MVP Hefesto)

Coolify clona la rama `coolify` y usa `compose.yaml` directamente; `compose.bootstrap.yaml` es solo bootstrap local y no se monta en Coolify. El build pack es Docker Compose con Traefik delante (TLS y dominio), así que el servicio `app` se conecta por la red interna de Docker y solo expone el puerto `8000` (sin `ports:`). El nombre del proyecto lo pone Coolify; este compose ya no fuerza `name:` ni el prefijo de los volúmenes sin un valor.

Variables nuevas (con default que preserva el uso original):

| Variable            | Default            | Significado                                                                                                                                                                       |
| ------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DB_NAME`           | `postgres`         | Base Postgres dedicada a esta app en el Supabase compartido. Coolify la pone como `mvp_<slug>` para mantener la base aislada dentro del mismo cluster.                            |
| `DB_SSLMODE`        | `verify-full`      | Modo SSL para Paperless y `psql`. `verify-full` exige CA; `disable` la vuelve opcional (conexión dentro de la red Docker de Coolify, sin TLS).                                       |
| `VOLUME_PREFIX`     | `hefesto-archivo`  | Prefijo de los nombres de volúmenes persistentes. Coolify debe asignar uno por app para que los volúmenes no se pisen entre despliegues.                                              |
| `SUPABASE_DEDICATED_CONFIRMED` | `false` | Coolify debe ponerlo en `true` (la base dedicada la verifica `ops/preflight.sh`).                                                                                                |
| `SUPABASE_DATA_API_DISABLED`   | `false` | Coolify debe ponerlo en `true` (Data API apagada; `ops/preflight.sh` aborta si no).                                                                                                |

`POSTGRES_HOST` debe ser el host interno del Postgres compartido dentro de la red de Coolify (no `*.supabase.co`). Con `DB_SSLMODE=disable` no hace falta montar `certs/ca.crt` (la conexión viaja por la red interna de Docker sin TLS); con `verify-full` sí es obligatorio.

Chequeos automáticos antes de cada deploy: `bash scripts/coolify-check.sh` confirma que `compose.yaml` respeta el contrato (sin `ports:`/`container_name`/binds fuera del repo, sin `name:` raíz, `DB_NAME` y `DB_SSLMODE` llegan al render).
