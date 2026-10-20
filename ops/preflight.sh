#!/bin/sh
set -eu
[ "$SUPABASE_DEDICATED_CONFIRMED" = true ] || { echo 'Confirme proyecto Supabase exclusivo'; exit 1; }
[ "$SUPABASE_DATA_API_DISABLED" = true ] || { echo 'Desactive Data API y confirme variable'; exit 1; }
# La CA es obligatoria con sslmode=verify-ca o verify-full; los demas modos
# (disable/allow/prefer/require) no consultan el certificado del servidor
# (conexion dentro de la red Docker de Coolify).
case "${PGSSLMODE:-verify-full}" in
  verify-ca|verify-full) [ -s "$PGSSLROOTCERT" ] || { echo 'Falta certificado CA'; exit 1; } ;;
esac
export PGCONNECT_TIMEOUT=15
psql --no-psqlrc -v ON_ERROR_STOP=1 -f /opt/hefesto/preflight.sql
