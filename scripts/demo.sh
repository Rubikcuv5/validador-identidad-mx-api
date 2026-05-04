#!/usr/bin/env bash
set -e

BASE_URL="http://localhost:8000"
CURP="BADD110313HCMLNS09"

# Levantar servidor en background
source .venv/bin/activate
uvicorn app.main:app --port 8000 &
SERVER_PID=$!
sleep 2

echo "=== 1. Validar CURP (primera vez, sin cache) ==="
curl -s -X POST "$BASE_URL/validate" \
  -H "Content-Type: application/json" \
  -d "{\"document\": \"$CURP\", \"doc_type\": \"CURP\"}" | python3 -m json.tool

echo ""
echo "=== 2. Validar mismo CURP (segunda vez, con cache) ==="
curl -s -X POST "$BASE_URL/validate" \
  -H "Content-Type: application/json" \
  -d "{\"document\": \"$CURP\", \"doc_type\": \"CURP\"}" | python3 -m json.tool

echo ""
echo "=== 3. Historial de auditoría ==="
curl -s "$BASE_URL/history" | python3 -m json.tool

kill $SERVER_PID 2>/dev/null
echo ""
echo "Demo completado."
