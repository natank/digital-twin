#!/usr/bin/env bash
# Local Phase 2 demo smoke (API must be running on :8000; seed applied).
set -euo pipefail
BASE="${API_URL:-http://localhost:8000}"
PASS="${SEED_PASSWORD:-Owner123!}"
EMAIL="${SEED_EMAIL:-owner@example.com}"

echo "== health =="
curl -sf "$BASE/health" | head -c 200; echo

echo "== login =="
TOKEN=$(curl -sf -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
OWNER=$(curl -sf "$BASE/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
echo "owner=$OWNER"

echo "== config =="
curl -sf "$BASE/config/me" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

echo "== chat =="
SID=$(curl -sf -X POST "$BASE/chat/sessions" \
  -H 'Content-Type: application/json' \
  -d "{\"owner_id\":\"$OWNER\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['session_id'])")
curl -sf -X POST "$BASE/chat/sessions/$SID/messages" \
  -H 'Content-Type: application/json' \
  -d '{"content":"What is your background?"}' | python3 -m json.tool | head -40

echo "== notifications =="
curl -sf "$BASE/notifications/me" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -40
echo "OK phase2 session=$SID"
