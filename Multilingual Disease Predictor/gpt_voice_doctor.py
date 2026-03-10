import os
import pickle
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
from deep_translator import GoogleTranslator
from langdetect import detect

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

engine = pyttsx3.init()

def speak(text):
    # Remove long paragraphs for better speech
    short_text = text.replace("\n", " ")
    print("\nAI Doctor:", short_text)
    engine.say(short_text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text
    except:
        return ""

def translate_to_english(text):
    try:
        language = detect(text)
        if language != "en":
            return GoogleTranslator(source='auto', target='en').translate(text)
        return text
    except:
        return text

def predict_disease(symptoms_text):
    symptoms_vector = vectorizer.transform([symptoms_text])
    prediction = model.predict(symptoms_vector)[0]
    probability = max(model.predict_proba(symptoms_vector)[0])
    return prediction, probability

# Conversation memory
messages = [
    {"role": "system", "content": "You are a friendly AI medical assistant. Talk casually and ask about symptoms in detail before diagnosing."}
]

speak("Hello! I'm your AI health assistant. How are you feeling today?")

conversation_text = ""

while True:
    user_input = listen()
    if user_input == "":
        continue

    conversation_text += user_input + " "

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    speak(reply)

    # If GPT decides enough info gathered
    if "diagnose" in reply.lower() or "analysis" in reply.lower():
        break

    # Safety stop
    if len(messages) > 12:
        break

# After conversation → Predict
processed_text = translate_to_english(conversation_text)
disease, prob = predict_disease(processed_text)

speak(f"Based on your symptoms, you may have {disease}.")
speak(f"My confidence level is {round(prob*100,2)} percent.")
speak("Please consult a medical professional for proper diagnosis.")
