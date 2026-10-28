curl -X POST \
  "$PRIMEAGENT_SERVER_URL/api/v1/responses" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-PRIMEAGENT-GLOBAL-VAR-OPENAI_API_KEY: sk-..." \
  -H "X-PRIMEAGENT-GLOBAL-VAR-USER_ID: user123" \
  -H "X-PRIMEAGENT-GLOBAL-VAR-ENVIRONMENT: production" \
  -d '{
    "model": "your-flow-id",
    "input": "Hello"
  }'
