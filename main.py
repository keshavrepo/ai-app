from fastapi import FastAPI, UploadFile
from PIL import Image
import pytesseract
import requests
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

class ChatRequest(BaseModel):
    message: str

app = FastAPI()

# ✅ Tesseract path (check correct ho)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ NEW API KEY 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def ask_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        # ✅ stable model
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": f"Explain clearly or solve this:\n{text}"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()

        print("API RESPONSE:", res_json)  # debug

        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]
        else:
            return "API Error: " + str(res_json)

    except Exception as e:
        return "Request Failed: " + str(e)


@app.post("/analyze")
async def analyze(file: UploadFile):
    try:
        image = Image.open(file.file)

        # OCR
        text = pytesseract.image_to_string(image)

        print("EXTRACTED TEXT:", text)  # debug

        if not text.strip():
            return {
                "text": "",
                "ai": "No text detected in image"
            }

        ai_response = ask_ai(text)

        return {
            "text": text,
            "ai": ai_response
        }

    except Exception as e:
        return {
            "error": str(e)
        }
@app.post("/chat")
async def chat(req: ChatRequest):
    reply = ask_ai(req.message)
    return {"reply": reply}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>AI Chat</title>
        <style>
            body {
                font-family: Arial;
                background: #0f172a;
                color: white;
                display: flex;
                flex-direction: column;
                height: 100vh;
                margin: 0;
            }
            #chat {
                flex: 1;
                padding: 10px;
                overflow-y: auto;
            }
            .msg {
                margin: 10px;
                padding: 10px;
                border-radius: 10px;
                max-width: 70%;
            }
            .user {
                background: #2563eb;
                align-self: flex-end;
            }
            .ai {
                background: #1e293b;
                align-self: flex-start;
            }
            #input {
                display: flex;
                padding: 10px;
                background: #020617;
            }
            input {
                flex: 1;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
            button {
                margin-left: 10px;
                padding: 10px;
                background: #22c55e;
                border: none;
                border-radius: 8px;
                color: white;
            }
        </style>
    </head>
    <body>

        <div id="chat"></div>

        <div id="input">
            <input id="msg" placeholder="Ask something..." />
            <button onclick="send()">Send</button>
        </div>

        <script>
            async function send() {
                let msg = document.getElementById("msg").value;

                let chat = document.getElementById("chat");

                chat.innerHTML += `<div class="msg user">${msg}</div>`;

                let res = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: msg })
                });

                let data = await res.json();

                chat.innerHTML += `<div class="msg ai">${data.reply}</div>`;

                document.getElementById("msg").value = "";
                chat.scrollTop = chat.scrollHeight;
            }
        </script>

    </body>
    </html>
    """
