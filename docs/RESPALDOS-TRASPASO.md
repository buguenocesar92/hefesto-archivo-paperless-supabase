# Respaldo completo
Detener ingreso de archivos y esperar que finalice OCR pendiente antes de respaldar. `python3 scripts/backup.py` detiene app, exporta public, guarda data/media/consume/export y broker, y copia configuración con checksums. Intenta reiniciar servicios al terminar; revisar salida, manifest completed y salud. El timeout de parada120s no garantiza finalizar OCR largo: vaciar cola primero.

Supabase solo guarda base: su respaldo no incluye originales/documentos del VPS. Guardar todo el conjunto, claves y repo/ZIP. Cifrar y copiar fuera del servidor con retención acordada. No se configura cifrado, destino remoto, cron ni limpieza automática.

## Recuperación aislada
1. Preparar proyecto Supabase nuevo con SQL inicial y rol, mismas versiones y volúmenes VACÍOS.
2. Recuperar .env preservando PAPERLESS_SECRET_KEY y claves necesarias. Ajustar host/usuario/CA, proyecto y prefijo de volúmenes para evitar tocar origen.
3. No arrancar app. Ejecutar `python3 scripts/restore_db.py /ruta/respaldo`.
4. Ejecutar `python3 scripts/restore_files.py /ruta/respaldo` con app/broker detenidos. Valida hashes, rechaza rutas/tipos inseguros y volúmenes no vacíos; no borra contenido.
5. El formato soportado contiene archivos/directorios normales. Si una personalización añadió enlaces simbólicos, el restaurador se detendrá: revisar esa personalización y su recuperación, no omitir la validación a ciegas.
6. Si una extracción falla parcialmente, usar otros volúmenes nuevos tras diagnosticar. No reintentar sobre datos parciales como si estuvieran vacíos.
7. Aislar salida externa en copia de pruebas: pueden restaurarse buzones/credenciales/colas. Verificar configuración antes de reanudar procesos.
8. Arrancar bootstrap y comprobar documentos, originales, búsqueda, permisos y trabajos pendientes. Reindexar con comando nativo si la documentación de esa versión lo requiere.

Solo restaurar respaldos propios confiables. No ejecutar DROP SCHEMA, db reset o down -v sobre datos reales. Una restauración de cola puede requerir revisar trabajos pendientes/duplicados; no prometer ejecución exactamente una vez.

## Actualizar/entregar
Respaldar y ensayar versión destino antes de cambiar imagen. Las migraciones pueden impedir rollback sin restauración de base/archivos compatibles.

Entregar proyecto Supabase, infraestructura/Coolify, repo, DNS, volúmenes, imágenes/digests, CA, claves y administrador actual, taxonomía, permisos y respaldo probado. Secretos por gestor seguro. El respaldo restaura Paperless; no es conversor automático a Odoo u otro gestor.
