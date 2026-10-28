curl -X GET \
  "$PRIMEAGENT_URL/api/v1/projects/download/$PROJECT_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  --output primeagent-project.zip
