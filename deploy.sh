#!/bin/bash
set -e
cd "$(dirname "$0")"

MSG="${1:-update}"

set -a
source .env
set +a

echo "==> git add + commit"
git add -A
if git diff --cached --quiet; then
    echo "(sin cambios para commitear)"
else
    git commit -m "$MSG"
fi

echo "==> git push"
git push origin main

echo "==> trigger deploy en PythonAnywhere"
RESP=$(curl -sS -X POST -H "X-Deploy-Token: $DEPLOY_TOKEN" "$DEPLOY_URL")
echo "$RESP" | python3 -m json.tool || echo "(respuesta no-JSON): $RESP"

OK=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('ok') else 'no')" 2>/dev/null)
if [ "$OK" != "yes" ]; then
    echo "==> ERROR: webhook fallo. Revisar respuesta arriba."
    exit 1
fi

echo ""
echo "==> LISTO"
