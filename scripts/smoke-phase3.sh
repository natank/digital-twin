#!/usr/bin/env bash
# Local Phase 3 smoke: public home/chat + owner dashboard APIs.
# API must be running on :8000; seed applied. Frontend optional (:4200).
set -euo pipefail
BASE="${API_URL:-http://localhost:8000}"
PASS="${SEED_PASSWORD:-Owner123!}"
EMAIL="${SEED_EMAIL:-owner@example.com}"
FE="${FRONTEND_URL:-http://localhost:4200}"

echo "== health =="
curl -sf "$BASE/health" | head -c 200; echo

echo "== login =="
TOKEN=$(curl -sf -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
OWNER=$(curl -sf "$BASE/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
echo "owner=$OWNER"

echo "== config =="
curl -sf "$BASE/config/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print('tone=', d.get('tone'))"

echo "== profile =="
curl -sf "$BASE/profiles/me" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print('headline=', d.get('headline'), 'has_cv=', d.get('has_cv'))"

echo "== notifications unread =="
curl -sf "$BASE/notifications/me/unread-count" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -10

echo "== conversations =="
curl -sf "$BASE/chat/me/conversations?limit=5" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print('total=', d.get('total'), 'items=', len(d.get('items') or []))"

echo "== public chat session =="
SID=$(curl -sf -X POST "$BASE/chat/sessions" \
  -H 'Content-Type: application/json' \
  -d "{\"owner_id\":\"$OWNER\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['session_id'])")
curl -sf -X POST "$BASE/chat/sessions/$SID/messages" \
  -H 'Content-Type: application/json' \
  -d '{"content":"What is your background?"}' | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print('reply_len=', len(d['reply']['content']))"

if curl -sf -o /dev/null "$FE/"; then
  echo "== frontend =="
  echo "OK frontend reachable at $FE"
else
  echo "== frontend =="
  echo "skip (not running at $FE)"
fi

echo "OK phase3 owner=$OWNER session=$SID"
