# Despliegue
Realizar bootstrap privado del README antes de publicar. La imagen crea hefesto_admin desde las variables iniciales y no restablece la contraseña de un usuario existente en cada arranque. Guardar la clave actual en gestor seguro y comprobar login tras cambiarla.

1. Detener bootstrap con `docker compose -f compose.yaml -f compose.bootstrap.yaml down` SIN -v.
2. Subir archivos versionables a repo privado sin .env/backups.
3. Crear recurso Compose usando compose.yaml; configurar variables y mismos nombres de volúmenes.
4. Colocar certs/ca.crt en el directorio del recurso y mantener ops/ disponible.
5. Asociar https://archivo.cliente.cl solo a app, puerto8000. Broker y dbtools no se publican.
6. Desplegar y verificar preflight, migraciones, login, subida y OCR. No confundir healthcheck HTTP con procesamiento documental correcto.

Revisar configuración de proxy según documentación si hay errores de CSRF/IP; mantener origen HTTPS y evitar proxies confiables indiscriminados. PAPERLESS_URL define origen esperado.

La captura periódica de correo está desactivada. Configurar correo entrante/saliente y reglas solo después de pruebas y autorización. No se enviaron correos ni se conectaron buzones.

Los volúmenes consume/export son internos; el flujo inicial recomendado es subir desde la interfaz. Un escáner no queda conectado automáticamente. Si se desea carpeta de red, diseñar permisos/ruta y cola antes de montarla; no publicar consume sin control.

Valkey guarda RDB y no tiene AOF en esta configuración. Un cierre abrupto puede perder cambios de cola posteriores al último snapshot. El backup fuerza SAVE; acordar objetivos de recuperación y validar durabilidad adicional si hace falta.
