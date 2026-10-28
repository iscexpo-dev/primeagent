import os

import requests

url = f"{os.getenv('PRIMEAGENT_SERVER_URL', '')}/api/v1/responses"

headers = {
    "x-api-key": f"{os.getenv('PRIMEAGENT_API_KEY', '')}",
    "Content-Type": "application/json",
    "X-PRIMEAGENT-GLOBAL-VAR-OPENAI_API_KEY": "sk-...",
    "X-PRIMEAGENT-GLOBAL-VAR-USER_ID": "user123",
    "X-PRIMEAGENT-GLOBAL-VAR-ENVIRONMENT": "production",
}

payload = {"model": "your-flow-id", "input": "Hello"}

response = requests.request("POST", url, headers=headers, json=payload)
response.raise_for_status()

print(response.text)
