curl -X GET \
  "$PRIMEAGENT_URL/api/v1/users/?skip=0&limit=10" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
