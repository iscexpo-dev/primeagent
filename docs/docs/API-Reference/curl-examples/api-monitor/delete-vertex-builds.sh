curl -X DELETE \
  "$PRIMEAGENT_URL/api/v1/monitor/builds?flow_id=$FLOW_ID" \
  -H "accept: */*" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
