curl -X POST \
  "$PRIMEAGENT_SERVER_URL/api/v1/webhook/$FLOW_ID" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -d '{"data": "example-data"}'
