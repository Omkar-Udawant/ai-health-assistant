import os
import pickle
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from langdetect import detect
import sqlite3
import datetime
import requests
import warnings

warnings.filterwarnings('ignore')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load ML model
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, "model.pkl")
vectorizer_path = os.path.join(base_dir, "vectorizer.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

# Database Setup
db_path = os.path.join(base_dir, "database.db")
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            input_text TEXT,
            output_text TEXT,
            confidence REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="AI Doctor Bot")

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

class DiagnoseRequest(BaseModel):
    user_texts: List[str]

def translate_to_english(text):
    try:
        language = detect(text)
        if language != "en":
            return GoogleTranslator(source='auto', target='en').translate(text)
        return text
    except Exception:
        return text

def do_predict_disease(symptoms_text):
    symptoms_vector = vectorizer.transform([symptoms_text])
    prediction = model.predict(symptoms_vector)[0]
    probability = float(max(model.predict_proba(symptoms_vector)[0]))
    return prediction, probability

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        system_msg = {"role": "system", "content": "You are a friendly AI medical assistant. Talk casually, ask about symptoms in detail, and maintain a highly professional, caring tone. Keep responses somewhat concise so they read like a chat."}
        msgs = [system_msg] + req.messages
        
        # Convert chat history for Ollama
        ollama_messages = []
        for m in msgs:
            ollama_messages.append({
                "role": m.get("role"),
                "content": m.get("content")
            })

        # Request to local Ollama server
        try:
            ollama_resp = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": ollama_messages,
                    "stream": False
                },
                timeout=30
            )
            ollama_resp.raise_for_status()
            reply = ollama_resp.json().get("message", {}).get("content", "Sorry, I couldn't formulate a response.")
        except requests.exceptions.RequestException as req_e:
            raise HTTPException(status_code=503, detail=f"Failed to connect to Local AI (Ollama). Ensure it is running. Error: {str(req_e)}")
            
        # Log to Database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            user_input = req.messages[-1]["content"] if req.messages else ""
            cursor.execute(
                "INSERT INTO interactions (timestamp, type, input_text, output_text, confidence) VALUES (?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), "chat", user_input, reply, 0.0)
            )
            conn.commit()
            conn.close()
        except Exception as db_e:
            print(f"Database logging error: {db_e}")

        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diagnose")
async def diagnose_endpoint(req: DiagnoseRequest):
    try:
        conversation_text = " ".join(req.user_texts)
        if not conversation_text.strip():
            return {"disease": "Unknown", "confidence": 0.0}
            
        processed_text = translate_to_english(conversation_text)
        disease, prob = do_predict_disease(processed_text)
        
        confidence_pct = round(prob * 100, 2)

        # Log to Database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO interactions (timestamp, type, input_text, output_text, confidence) VALUES (?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), "diagnosis", conversation_text, disease, confidence_pct)
            )
            conn.commit()
            conn.close()
        except Exception as db_e:
            print(f"Database logging error: {db_e}")
        
        return {
            "disease": disease,
            "confidence": confidence_pct
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend
frontend_dir = os.path.join(base_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
