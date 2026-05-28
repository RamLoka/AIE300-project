import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "What is Docker in one sentence?",
        "stream": False
    }
)

data = response.json()

print(data["response"])