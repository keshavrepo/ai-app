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
        <title>HelperShot AI</title>

        <style>
            body {
                margin: 0;
                font-family: Arial;
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
            }

            .msg {
                max-width: 65%;
                padding: 12px;
                margin: 10px;
                border-radius: 12px;
                line-height: 1.5;
            }

            .user {
                background: #2563eb;
                margin-left: auto;
            }

            .bot {
                background: #1e293b;
            }

            #inputBox {
                display: flex;
                flex-direction: column;
                padding: 10px;
                background: #020617;
            }

            #row {
                display: flex;
                margin-top: 5px;
            }

            input[type="text"] {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                outline: none;
            }

            button {
                margin-left: 10px;
                padding: 12px;
                background: #22c55e;
                border: none;
                color: white;
                border-radius: 8px;
                cursor: pointer;
            }

            button:hover {
                background: #16a34a;
            }

            input[type="file"] {
                margin-bottom: 5px;
                color: white;
            }
        </style>
    </head>

    <body>

        <div id="chat"></div>

        <div id="inputBox">
            <input type="file" id="imageInput" />

            <div id="row">
                <input id="msg" placeholder="Ask anything..." />
                <button onclick="send()">Send</button>
                <button onclick="uploadImage()">📷</button>
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

            async function uploadImage() {
                let fileInput = document.getElementById("imageInput");
                let file = fileInput.files[0];

                if (!file) {
                    alert("Image select kar bhai");
                    return;
                }

                let formData = new FormData();
                formData.append("file", file);

                let chat = document.getElementById("chat");
                chat.innerHTML += `<div class='msg user'>📷 Image Uploaded</div>`;

                let res = await fetch("/analyze", {
                    method: "POST",
                    body: formData
                });

                let data = await res.json();

                chat.innerHTML += `<div class='msg bot'>${data.ai}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }
        </script>

    </body>
    </html>
    """