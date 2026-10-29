curl -X DELETE \
  "$PRIMEAGENT_URL/api/v2/files/$FILE_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
