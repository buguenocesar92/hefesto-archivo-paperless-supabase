#!/bin/sh
set -eu
[ "$SUPABASE_DEDICATED_CONFIRMED" = true ] || { echo 'Confirme proyecto Supabase exclusivo'; exit 1; }
[ "$SUPABASE_DATA_API_DISABLED" = true ] || { echo 'Desactive Data API y confirme variable'; exit 1; }
# La CA solo es obligatoria cuando sslmode=verify-full; con DB_SSLMODE=disable/prefer/require
# el certificado del servidor no se consulta (conexion dentro de la red Docker de Coolify).
if [ "${DB_SSLMODE:-verify-full}" = "verify-full" ]; then
  [ -s "$PGSSLROOTCERT" ] || { echo 'Falta certificado CA'; exit 1; }
fi
export PGCONNECT_TIMEOUT=15
psql --no-psqlrc -v ON_ERROR_STOP=1 -f /opt/hefesto/preflight.sql
