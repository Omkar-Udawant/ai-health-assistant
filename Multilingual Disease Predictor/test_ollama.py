import messages
import ollama
import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3",
        "messages": messages,
        "stream": False
    }
)

reply = response.json()["message"]["content"]

messages = [
    {"role": "system", "content":
     "You are a friendly AI health assistant speaking in voice mode. "
     "Speak casually like a human doctor. "
     "Keep responses short and conversational. "
     "Ask only one question at a time. "
     "Do not give long explanations. "
     "Talk like you are having a natural conversation. "
     "Be warm and empathetic."}
]

print(response['message']['content'])