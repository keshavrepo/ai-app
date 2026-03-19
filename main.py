from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://helpershot.vercel.app "],  # sab allow karega
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        <title>HelperShot AI</title>

        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: #0f172a;
                color: white;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }

            #chat {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
            }

            .msg {
                max-width: 70%;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 12px;
                font-size: 14px;
                line-height: 1.5;
                animation: fadeIn 0.2s ease-in;
            }

            .user {
                background: #2563eb;
                align-self: flex-end;
            }

            .bot {
                background: #1e293b;
                align-self: flex-start;
            }

            #inputBox {
                padding: 10px;
                background: #020617;
                border-top: 1px solid #1e293b;
            }

            #row {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            input[type="text"] {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 10px;
                outline: none;
                font-size: 14px;
            }

            button {
                padding: 10px 14px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                font-weight: bold;
            }

            .sendBtn {
                background: #22c55e;
                color: white;
            }

            .uploadBtn {
                background: #334155;
                color: white;
            }

            input[type="file"] {
                display: none;
            }

            label {
                background: #334155;
                padding: 10px;
                border-radius: 10px;
                cursor: pointer;
            }

            @keyframes fadeIn {
                from {opacity: 0; transform: translateY(5px);}
                to {opacity: 1; transform: translateY(0);}
            }
        </style>
    </head>

    <body>

        <div id="chat"></div>

        <div id="inputBox">

            <div id="row">
                <label for="imageInput">📷</label>
                <input type="file" id="imageInput"/>

                <input id="msg" placeholder="Ask anything..." />

                <button class="sendBtn" onclick="send()">Send</button>
            </div>
        </div>

        <script>
            async function send() {
                let input = document.getElementById("msg");
                let chat = document.getElementById("chat");

                let userMsg = input.value;
                if (!userMsg) return;

                chat.innerHTML += `<div class='msg user'>${userMsg}</div>`;
                input.value = "";

                let res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: userMsg})
                });

                let data = await res.json();

                chat.innerHTML += `<div class='msg bot'>${data.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }

            document.getElementById("imageInput").addEventListener("change", async function() {
                let file = this.files[0];
                if (!file) return;

                let chat = document.getElementById("chat");
                chat.innerHTML += `<div class='msg user'>📷 Image Uploaded</div>`;

                let formData = new FormData();
                formData.append("file", file);

                let res = await fetch("/analyze", {
                    method: "POST",
                    body: formData
                });

                let data = await res.json();

                chat.innerHTML += `<div class='msg bot'>${data.ai}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });
        </script>

    </body>
    </html>
    """