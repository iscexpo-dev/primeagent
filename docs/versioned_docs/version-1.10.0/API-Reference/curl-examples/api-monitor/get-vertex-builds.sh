curl -X GET \
  "$PRIMEAGENT_URL/api/v1/monitor/builds?flow_id=$FLOW_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
