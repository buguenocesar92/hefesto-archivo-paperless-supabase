# Preparación de base
Crear proyecto Supabase NUEVO dedicado a Paperless, PostgreSQL16/17 y región cercana al VPS. No reutilizar la base de otra aplicación ni activar RLS de otro producto sobre estas tablas.

Ejecutar sql/01-supabase.sql como postgres en SQL Editor. Exige public vacío y crea paperless_app. Asignar la clave generada de .env al rol desde psql administrativo usando `\password paperless_app`. Mantener credenciales administrativas fuera del runtime.

Usar conexión directa5432; si el VPS requiere IPv4, pooler en modo SESSION5432 con usuario paperless_app.PROJECT_REF conforme a datos del proyecto. No usar transaction6543. Base postgres; CA válida para hostname en certs/ca.crt. Pooler y conexión directa pueden requerir cadenas CA distintas.

Deshabilitar Data API. El SQL restringe permisos para anon/authenticated; el preflight comprueba propiedad, permisos y marcadores básicos, pero las variables de confirmación no consultan la API administrativa. No proporcionar claves DB o service_role al frontend.

Los procesos Django/Celery y sus pools pueden abrir varias conexiones. pool.max_size=5 es por pool, no un máximo global de la instalación. Ajustar capacidad y vigilar límites. La aplicación ejecuta migraciones al iniciar; no arrancar dos instancias durante una actualización.

No habilitar pgvector ni servicios de IA por defecto: este paquete se limita al OCR/búsqueda nativos. Si una futura función requiere extensión/proveedor, revisarla antes de habilitarla.
