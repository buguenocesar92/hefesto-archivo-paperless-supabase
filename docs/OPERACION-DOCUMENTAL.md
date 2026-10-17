# Organización y flujo
## Preparar
Crear tipos documentales, remitentes y etiquetas, por ejemplo: proveedor, contrato, comprobante, procedimiento, pendiente de revisión y archivado. Definir propietario y grupos antes de cargar datos reales.

## Flujo
Recepción → verificar archivo/origen → subir → esperar procesamiento → comprobar OCR, título, fecha y remitente → asignar permisos/etiquetas → revisar búsqueda y descarga → archivar según política.

OCR spa+eng es local. Modo skip evita rehacer OCR donde ya hay texto; para comprobar reconocimiento real probar un escaneo de imagen sin capa de texto. Acentos, tablas, escritura manual y páginas borrosas pueden fallar. Los resultados deben revisarse; no usar texto extraído como prueba automática de exactitud.

Paperless conserva originales y archivos procesados según flujo nativo. No borrar originales externos ni asumir que PDF/A o una búsqueda equivalen a firma/autenticidad documental. Duplicados deben resolverse con criterio, no mediante borrado masivo.

## Permisos
Administrador para configuración; operador para carga/revisión; lector para documentos autorizados. Probar con usuarios sin privilegios, acceso directo a original/archivado y enlaces compartidos. Un superusuario ve más que un usuario normal y no sirve para validar restricciones.

Permisos por documento/propietario deben configurarse y comprobarse. Instancias separadas son preferibles cuando cada cliente necesita administradores independientes. El ZIP no implementa multitenencia propia.

## Datos y procesamiento externo
No se configuró proveedor LLM externo. No habilitar integración de IA/buzón/webhook sin evaluar qué datos transmite y quién puede acceder. OCR no es anonimización: ocultar texto en pantalla no elimina datos del PDF original ni de sus metadatos.

## Límites
No incluye Office mediante Tika/Gotenberg, expedientes legales especializados, firma electrónica, ARCOP automatizado ni certificación de conservación. Integraciones con Odoo/Nextcloud/Supabase Storage requieren trabajo separado.
