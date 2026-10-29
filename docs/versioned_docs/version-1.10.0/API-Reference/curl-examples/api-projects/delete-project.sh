curl -X DELETE \
  "$PRIMEAGENT_URL/api/v1/projects/$PROJECT_ID" \
  -H "accept: */*" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
