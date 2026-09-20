#!/usr/bin/env bash
# Does the local OmniRoute accept /v1 traffic with no Authorization header?
C=mscast-poc-backend-1
H=host.docker.internal:20128

echo "=== GET /v1/models, no key ==="
docker exec "$C" bash -c "curl -s -m 10 -w '\n-- http %{http_code}\n' http://$H/v1/models" | head -c 1200

echo
echo "=== POST /v1/chat/completions, no key ==="
docker exec "$C" bash -c "curl -s -m 60 -w '\n-- http %{http_code}\n' \
  -X POST http://$H/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{\"model\":\"hermes-antigravity\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with the single word: ready\"}],\"max_tokens\":16}'" | head -c 1500
echo
