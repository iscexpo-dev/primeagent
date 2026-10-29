curl -X GET \
  "$PRIMEAGENT_URL/api/v1/monitor/transactions?flow_id=$FLOW_ID&page=1&size=50" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
