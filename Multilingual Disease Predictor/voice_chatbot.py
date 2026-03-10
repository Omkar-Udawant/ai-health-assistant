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
    print("AI Doctor:", text)
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

# -----------------------------
# Casual Conversation Flow
# -----------------------------

speak("Hi there! I'm your AI health assistant. How are you feeling today?")

conversation = ""
symptom_count = 0

while True:
    user_input = listen()
    if user_input == "":
        continue

    conversation += user_input + " "
    symptom_count += 1

    # Casual responses
    if symptom_count == 1:
        speak("Oh okay. Since when are you feeling this way?")
    elif symptom_count == 2:
        speak("Hmm I see. Do you also have any body pain, nausea, or other discomfort?")
    elif symptom_count == 3:
        speak("Alright. Let me analyze your symptoms now.")
        break
    else:
        speak("Tell me more about how you're feeling.")

# -----------------------------
# Prediction Phase
# -----------------------------

processed_text = translate_to_english(conversation)
disease, prob = predict_disease(processed_text)

speak(f"Based on what you told me, you might have {disease}.")
speak(f"My confidence level is {round(prob*100,2)} percent.")

speak("I recommend consulting a nearby doctor and staying hydrated.")
speak("If symptoms worsen, please seek medical help immediately.")

