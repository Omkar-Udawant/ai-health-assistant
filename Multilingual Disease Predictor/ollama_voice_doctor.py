import requests
import json
import pickle
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
from langdetect import detect

# Load ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

engine = pyttsx3.init()

def speak(text):
    engine.setProperty('rate', 170)   # Speed
    engine.setProperty('volume', 1.0) # Volume

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Try voices[1] if needed

    engine.say(text)
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
    {"role": "system", "content":
     "You are a friendly AI health assistant. "
     "Talk naturally and casually. Ask follow-up questions. "
     "When user says 'check my health' or 'analyze my symptoms', "
     "stop asking questions and say 'Analyzing now.'"}
]

speak("Hi! I'm your AI health assistant. How are you feeling today?")

conversation_text = ""

while True:
    user_input = listen()

    if user_input == "":
        continue

    # Exit condition
    if "exit" in user_input.lower():
        speak("Take care! Wishing you good health.")
        break

    conversation_text += user_input + " "
    messages.append({"role": "user", "content": user_input})

    # If user wants diagnosis
    if "check my health" in user_input.lower() or "analyze my symptoms" in user_input.lower():
        speak("Analyzing your symptoms now.")
        break

    # Normal conversation
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3",
        "messages": messages,
        "stream": False
    }
)

reply = response.json()["message"]["content"]


# --------------------------
# Diagnosis Phase
# --------------------------

processed_text = translate_to_english(conversation_text)
disease, prob = predict_disease(processed_text)

speak(f"Based on what you told me, you may have {disease}.")
speak(f"My confidence level is {round(prob*100,2)} percent.")
speak("Please consult a medical professional for proper diagnosis.")
