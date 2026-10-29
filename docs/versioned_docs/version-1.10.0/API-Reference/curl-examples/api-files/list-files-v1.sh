curl -X GET \
  "$PRIMEAGENT_URL/api/v1/files/list/$FLOW_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
