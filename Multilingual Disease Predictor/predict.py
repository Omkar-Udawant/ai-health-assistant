import pickle
from deep_translator import GoogleTranslator
from langdetect import detect

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


def translate_to_english(text):
    language = detect(text)

    if language != "en":
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    return text


def predict_disease(symptoms_text):
    symptoms_vector = vectorizer.transform([symptoms_text])
    prediction = model.predict(symptoms_vector)[0]
    probability = max(model.predict_proba(symptoms_vector)[0])
    return prediction, probability


# Take input
user_input = input("Enter symptoms: ")

# Detect & translate
processed_input = translate_to_english(user_input)

print("Processed Input (English):", processed_input)

# Predict
disease, prob = predict_disease(processed_input)

print("\nPredicted Disease:", disease)
print("Confidence:", round(prob * 100, 2), "%")