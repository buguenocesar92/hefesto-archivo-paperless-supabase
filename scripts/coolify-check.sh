#!/usr/bin/env bash
# scripts/coolify-check.sh — valida que compose.yaml cumpla los puntos 1 y 2
# del contrato Coolify y, como esta app usa bd: supabase-pg, que DB_NAME y
# DB_SSLMODE parametrizables viajen al render.
#
# Salida: 0 si todo cumple; distinto de 0 listando "servicio: motivo".

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/compose.yaml"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Falta ${COMPOSE_FILE}" >&2
  exit 1
fi

fail=0

# 1) .env temporal con un valor ficticio por cada ${VAR} del compose.
TMP_ENV="$(mktemp -t coolify-check.XXXXXX.env)"
trap 'rm -f "${TMP_ENV}"' EXIT

VARS="$(grep -oE '\$\{[A-Z_][A-Z0-9_]*(:\?|:[?-][^}]*)?\}' "${COMPOSE_FILE}" \
  | sed -E 's/^\$\{([A-Z_][A-Z0-9_]*).*/\1/' | sort -u)"

for v in ${VARS}; do
  case "${v}" in
    POSTGRES_HOST|ARCHIVE_HOST) echo "${v}=https://ejemplo.invalid" >> "${TMP_ENV}" ;;
    ADMIN_EMAIL)                echo "${v}=admin@ejemplo.invalid"     >> "${TMP_ENV}" ;;
    DB_NAME)                    echo "${v}=mvp_prueba"                >> "${TMP_ENV}" ;;
    DB_SSLMODE)                 echo "${v}=disable"                   >> "${TMP_ENV}" ;;
    *)                          echo "${v}=x1234567890abcdef"        >> "${TMP_ENV}" ;;
  esac
done

# 2) Render del compose con el .env ficticio.
RENDER="$(docker compose --project-directory "${REPO_ROOT}" -f "${COMPOSE_FILE}" \
  --env-file "${TMP_ENV}" config --format json)"

# 3) Comprobaciones del contrato sobre los servicios sin profiles.
for svc in $(echo "${RENDER}" | jq -r '.services | keys[]'); do
  svc_json="$(echo "${RENDER}" | jq ".services.\"${svc}\"")"
  profiles="$(echo "${svc_json}" | jq -r '.profiles // [] | join(" ")')"
  [[ -n "${profiles}" ]] && continue

  # 1.a Sin ports (Coolify enruta vía Traefik).
  if echo "${svc_json}" | jq -e 'has("ports")' >/dev/null; then
    echo "${svc}: expone 'ports' (Coolify enruta por Traefik)" >&2
    fail=1
  fi
  # 1.b Sin container_name.
  if echo "${svc_json}" | jq -e 'has("container_name")' >/dev/null; then
    echo "${svc}: define 'container_name'" >&2
    fail=1
  fi
  # 1.c Sin privileged, cap_add, devices.
  for forbidden in privileged cap_add devices; do
    if echo "${svc_json}" | jq -e "has(\"${forbidden}\")" >/dev/null; then
      echo "${svc}: define '${forbidden}'" >&2
      fail=1
    fi
  done
  # 1.d Sin network_mode: host / pid: host / ipc: host / security_opt unconfined.
  if v="$(echo "${svc_json}" | jq -r '.network_mode // empty')"; [[ "${v}" == "host" ]]; then
    echo "${svc}: network_mode host" >&2; fail=1
  fi
  if v="$(echo "${svc_json}" | jq -r '.pid // empty')"; [[ "${v}" == "host" ]]; then
    echo "${svc}: pid host" >&2; fail=1
  fi
  if v="$(echo "${svc_json}" | jq -r '.ipc // empty')"; [[ "${v}" == "host" ]]; then
    echo "${svc}: ipc host" >&2; fail=1
  fi
  sec="$(echo "${svc_json}" | jq -c '.security_opt // []')"
  if [[ "${sec}" != "[]" ]] && echo "${sec}" | jq -e 'index("unconfined")' >/dev/null; then
    echo "${svc}: security_opt unconfined" >&2; fail=1
  fi

  # 1.e Binds prohibidos: docker.sock, rutas absolutas fuera del repo o con '..'.
  bind_violations=""
  while IFS= read -r src; do
    [[ -z "${src}" ]] && continue
    case "${src}" in
      *docker.sock*)
        bind_violations+="${svc}: bind docker.sock (${src})"$'\n'
        ;;
      "${REPO_ROOT}"/*)
        # bind dentro del repo: aceptable aunque la ruta quede absoluta
        :
        ;;
      /*)
        bind_violations+="${svc}: bind absoluto fuera del repo (${src})"$'\n'
        ;;
      *..*)
        bind_violations+="${svc}: bind que sale del repo (${src})"$'\n'
        ;;
    esac
  done < <(echo "${svc_json}" | jq -r '.volumes[]? | select(.type == "bind") | .source' 2>/dev/null || true)
  if [[ -n "${bind_violations}" ]]; then
    echo "${bind_violations}" >&2
    fail=1
  fi
done

# 4) name: en raíz → fija el proyecto (Coolify asigna el suyo).
#    Se mira en el source: Docker Compose puede añadir un 'name' al render si
#    COMPOSE_PROJECT_NAME está en el entorno, pero eso es automático y no fija.
if grep -qE '^name:' "${COMPOSE_FILE}"; then
  echo "raíz: define 'name:' en compose.yaml (Coolify asigna el nombre)" >&2
  fail=1
fi

# 5) Volúmenes con name: deben referenciar ${VOLUME_PREFIX} (parametrizable).
viol="$(awk '/^volumes:/,/^networks:/' "${COMPOSE_FILE}" \
  | grep -E '^[[:space:]]+name:' \
  | grep -vE '\$\{?VOLUME_PREFIX[?:}]' || true)"
if [[ -n "${viol}" ]]; then
  echo "volúmenes con 'name:' fijo (deben usar \${VOLUME_PREFIX}):" >&2
  echo "${viol}" >&2
  fail=1
fi

# 6) Redes con name: → fijo, no permitido.
net_viol="$(awk '/^networks:/,0' "${COMPOSE_FILE}" \
  | grep -E '^[[:space:]]+name:' || true)"
if [[ -n "${net_viol}" ]]; then
  echo "redes con 'name:' fijo:" >&2
  echo "${net_viol}" >&2
  fail=1
fi

# 7) supabase-pg: DB_NAME=mvp_prueba y DB_SSLMODE=disable en el render.
render_env="$(echo "${RENDER}" \
  | jq -r '[.. | objects | select(has("environment")) | .environment | to_entries[] | "\(.key)=\(.value)"] | join("\n")')"

if ! grep -qE '^(PGDATABASE|DB_NAME)=mvp_prueba$' <<< "${render_env}"; then
  echo "supabase-pg: DB_NAME=mvp_prueba no aparece en el render" >&2
  fail=1
fi
if ! grep -qE '(^PGSSLMODE=disable$|^DB_SSLMODE=disable$|sslmode=disable)' <<< "${render_env}"; then
  echo "supabase-pg: DB_SSLMODE=disable no aparece en el render" >&2
  fail=1
fi

if [[ "${fail}" -ne 0 ]]; then
  echo "coolify-check: FAIL" >&2
  exit 1
fi

echo "coolify-check: OK"