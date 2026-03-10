# Multilingual Disease Predictor 🩺🤖

A professional, state-of-the-art web application powered by **FastAPI**, **Machine Learning (Scikit-Learn)**, and **Ollama (Local LLMs)**. This project transforms a command-line script into a modern, visually stunning web-based AI Health Assistant that asks detailed medical questions, translates symptoms, and provides a preliminary diagnosis.

## 🌟 Key Features
* **100% Offline & Free API (Ollama):** The application relies on a local instance of Ollama (specifically the `llama3` model) to run the chatbot safely, privately, and for free! No more OpenAI API Quota errors!
* **High-Performance Backend:** Powered by FastAPI for robust API routing and quick AI inference.
* **Premium User Interface:** Uses Vanilla HTML/CSS/JS with absolutely jaw-dropping aesthetics—featuring dark mode, glassmorphism, dynamic gradients, and smooth slide-up micro-animations. 
* **Built-in Voice Assistance (Speech-to-Text & Text-to-Speech):** 
  * Just click the 🎤 **Mic** to speak your symptoms out loud natively in your browser.
  * The AI Assistant will reply to your questions and read its diagnosis back to you out loud!
* **Machine Learning Diagnosis:** Integrates your custom `vectorizer.pkl` and `model.pkl` to calculate confidence scores out of 100% and predict dozens of diseases.
* **Local Database Storage (SQLite):** Seamlessly records all your symptoms, the AI chats, and diagnostic confidence scores into `backend/database.db` automatically. 

---

## 🚀 Getting Started

### Prerequisites
Before running the project, you must ensure the following are installed:
1. **[Python 3.9+](https://www.python.org/downloads/)**
2. **[Ollama](https://ollama.com/)** ➡️ *You must have Ollama installed and running on your local machine.*

### 🛠 Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/multilingual-disease-predictor.git
cd "multilingual-disease-predictor"
```

**2. Download the Llama 3 Model**
Since this chatbot runs 100% locally, you need to pull the language model:
```bash
ollama pull llama3
```

**3. Install Python Dependencies**
```bash
pip install -r backend/requirements.txt
```

### ⚡ Running the Application

Start the web server:
```bash
python backend/main.py
```

1. Wait a moment for the server to boot up.
2. Open your web browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
3. Start talking to your AI assistant! 

> **Note:** The very first message you send might take a few seconds as the Llama3 model gets loaded into your computer's RAM.

---

## 🗂 Project Structure
```text
📦 Multilingual Disease Predictor
 ┣ 📂 backend/               # FastAPI Server & Python Logic
 ┃ ┣ 📜 main.py              # Application Entry Point & Routes
 ┃ ┣ 📜 database.db          # Auto-generated SQLite Session Logs
 ┃ ┣ 📜 requirements.txt     # Python Dependencies
 ┣ 📂 frontend/              # Web Interface
 ┃ ┣ 📜 index.html           # Premium User Layout
 ┃ ┣ 📜 style.css            # Dark mode, Glassmorphism, Animations
 ┃ ┣ 📜 app.js               # Logic, Fetch APIs, and Voice Synthesis
 ┣ 📜 model.pkl              # Pre-trained ML Prediction Model
 ┣ 📜 vectorizer.pkl         # Language TF-IDF Vectorizer
 ┗ 📜 README.md              # Documentation
```

## ⚠️ Disclaimer
This tool is for informational and educational purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified human health provider regarding a medical condition.
