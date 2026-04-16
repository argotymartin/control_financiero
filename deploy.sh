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
curl -sS -X POST \
    -H "X-Deploy-Token: $DEPLOY_TOKEN" \
    "$DEPLOY_URL" | python3 -m json.tool || echo "(respuesta no-JSON)"

echo ""
echo "==> LISTO"
