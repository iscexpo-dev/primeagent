curl -X GET \
  "$PRIMEAGENT_URL/api/v1/users/whoami" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY"
