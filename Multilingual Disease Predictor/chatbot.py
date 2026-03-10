import os
import pickle
from dotenv import load_dotenv
from openai import OpenAI
from deep_translator import GoogleTranslator
from langdetect import detect

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


def translate_to_english(text):
    language = detect(text)
    if language != "en":
        return GoogleTranslator(source='auto', target='en').translate(text)
    return text


def predict_disease(symptoms_text):
    symptoms_vector = vectorizer.transform([symptoms_text])
    prediction = model.predict(symptoms_vector)[0]
    probability = max(model.predict_proba(symptoms_vector)[0])
    return prediction, probability


def chat_with_ai(user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a friendly medical assistant. Ask about symptoms casually."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


# Chat loop
print("AI Doctor: Hello! Tell me how you are feeling today.")

conversation = ""

while True:
    user_input = input("You: ")
    conversation += user_input + " "

    if user_input.lower() == "done":
        break

    reply = chat_with_ai(user_input)
    print("AI Doctor:", reply)

# After conversation ends
processed_text = translate_to_english(conversation)
disease, prob = predict_disease(processed_text)

print("\n--- Diagnosis ---")
print("Predicted Disease:", disease)
print("Confidence:", round(prob * 100, 2), "%")