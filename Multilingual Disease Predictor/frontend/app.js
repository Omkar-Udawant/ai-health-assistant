const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const btnMic = document.getElementById('btn-mic');
const actionBar = document.getElementById('action-bar');
const modalOverlay = document.getElementById('diagnosis-modal');
const diagProgress = document.getElementById('diag-progress');

let messages = []; // Chat history for the backend
let userTexts = []; // Only user texts for the ML diagnosis
let isRecording = false;
let recognition = null;
let currentUtterance = null; // Track speech to avoid overlap

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US'; // We could detect language or set to auto if feasible, defaults to device lang often if omitted.

    recognition.onstart = function() {
        isRecording = true;
        btnMic.classList.add('recording');
        chatInput.placeholder = "Listening...";
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
        stopVoice();
    };

    recognition.onend = function() {
        stopVoice();
    };
} else {
    btnMic.style.display = 'none'; // Hide mic if not supported
}

function toggleVoice() {
    if (isRecording) {
        recognition.stop();
    } else {
        if (recognition) {
            recognition.start();
        } else {
            alert("Voice recognition not supported in this browser.");
        }
    }
}

function stopVoice() {
    isRecording = false;
    btnMic.classList.remove('recording');
    chatInput.placeholder = "Describe your symptoms...";
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Stop current speech
        
        // Strip out basic HTML or formatting for speech
        const plainText = text.replace(/<[^>]+>/g, '').replace(/\*/g, '');
        
        currentUtterance = new SpeechSynthesisUtterance(plainText);
        currentUtterance.lang = 'en-US';
        currentUtterance.rate = 1.0;
        currentUtterance.pitch = 1.0;
        
        // Try to pick a natural sounding voice if available
        const voices = window.speechSynthesis.getVoices();
        const googleVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Natural'));
        if (googleVoice) {
            currentUtterance.voice = googleVoice;
        }
        
        window.speechSynthesis.speak(currentUtterance);
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

function createTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message ai-message typing';
    div.id = 'typing-indicator';
    div.innerHTML = `
        <div class="avatar"><i class='bx bx-bot'></i></div>
        <div class="content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    return div;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append user message to UI
    appendMessage('user', text);
    chatInput.value = '';
    
    // Save to state
    messages.push({ role: 'user', content: text });
    userTexts.push(text);

    // Show Diagnosis Button after first message
    if (userTexts.length > 0) {
        actionBar.classList.remove('hidden');
    }

    // Show typing indicator
    const typing = createTypingIndicator();
    chatBox.appendChild(typing);
    scrollToBottom();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages })
        });
        
        const data = await response.json();
        
        // Remove typing
        chatBox.removeChild(document.getElementById('typing-indicator'));

        if (response.ok && data.reply) {
            appendMessage('ai', data.reply);
            speakText(data.reply);
            messages.push({ role: 'assistant', content: data.reply });
        } else {
            const errorMessage = data.detail || "Sorry, I encountered an internal server error. Please check the backend.";
            appendMessage('ai', errorMessage);
            speakText("I encountered an error.");
        }
    } catch (err) {
        console.error(err);
        chatBox.removeChild(document.getElementById('typing-indicator'));
        appendMessage('ai', "An error occurred while connecting to the server. Is it running?");
        speakText("An error occurred while connecting to the server.");
    }
}

function appendMessage(role, text) {
    const div = document.createElement('div');
    div.className = `message ${role}-message`;
    
    const avatar = role === 'ai' ? "<div class='avatar'><i class='bx bx-bot'></i></div>" : "<div class='avatar'><i class='bx bx-user'></i></div>";
    
    // Replace newlines with <br> for HTML rendering
    const formattedText = text.replace(/\n/g, '<br>');

    div.innerHTML = `
        ${avatar}
        <div class="content">
            <p>${formattedText}</p>
        </div>
    `;
    chatBox.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function getDiagnosis() {
    if (userTexts.length === 0) return;

    // Show loading modal
    document.getElementById('diag-disease').textContent = "Analyzing symptoms...";
    document.getElementById('diag-confidence-text').textContent = "Calculating";
    diagProgress.style.width = "0%";
    diagProgress.style.background = "linear-gradient(90deg, #6d5dfc, #8e82fe)";
    modalOverlay.classList.add('active');

    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_texts: userTexts })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('diag-disease').textContent = data.disease;
            document.getElementById('diag-confidence-text').textContent = `${data.confidence}%`;
            
            speakText(`Based on your symptoms, you may have ${data.disease}. My confidence level is ${data.confidence} percent. Please consult a human medical professional for a proper diagnosis.`);
            
            // Animate progress bar
            setTimeout(() => {
                const conf = parseFloat(data.confidence);
                diagProgress.style.width = `${conf}%`;
                
                // Color code based on confidence
                if (conf > 80) diagProgress.style.background = "linear-gradient(90deg, #10b981, #34d399)";
                else if (conf > 50) diagProgress.style.background = "linear-gradient(90deg, #f59e0b, #fbbf24)";
                else diagProgress.style.background = "linear-gradient(90deg, #ef4444, #f87171)";
            }, 300);

        } else {
            document.getElementById('diag-disease').textContent = "Error Diagnosis";
        }
    } catch (err) {
        console.error(err);
        document.getElementById('diag-disease').textContent = "Network Error";
    }
}

function closeModal() {
    modalOverlay.classList.remove('active');
}
