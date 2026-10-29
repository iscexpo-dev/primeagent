curl -X DELETE \
  "$PRIMEAGENT_URL/api/v1/files/delete/$FLOW_ID/2024-12-30_15-19-43_your_file.txt" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
