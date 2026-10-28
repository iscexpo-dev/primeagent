curl -X GET \
  "$PRIMEAGENT_URL/logs?lines_before=0&lines_after=0&timestamp=0" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
