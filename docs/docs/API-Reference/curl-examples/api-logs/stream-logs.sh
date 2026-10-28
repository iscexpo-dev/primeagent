curl -X GET \
  "$PRIMEAGENT_URL/logs-stream" \
  -H "accept: text/event-stream" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
