curl -N -X POST \
  "$PRIMEAGENT_SERVER_URL/api/v2/workflows" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -d '{
    "flow_id": "67ccd2be-17f0-8190-81ff-3bb2cf6508e6",
    "input_value": "Hello from a Primeagent stream client",
    "mode": "stream",
    "session_id": "session-123"
  }'
