import { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const chatRef = useRef();

  // AUTO SCROLL
  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  // SAFE TYPING FUNCTION
  const typeText = (text) => {
    let i = 0;

    // add empty bot message first
    setMessages((prev) => [...prev, { role: "bot", text: "" }]);

    const interval = setInterval(() => {
      i++;

      setMessages((prev) => {
        if (prev.length === 0) return prev;

        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "bot",
          text: text.slice(0, i),
        };

        return updated;
      });

      if (i >= text.length) {
        clearInterval(interval);
      }
    }, 20);
  };

  // SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const userInput = input;
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(
        "https://helpershot.onrender.com/chat",
        { message: userInput },
        {
          timeout: 120000,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setLoading(false);

      // fallback safety
      const reply = res?.data?.reply || "No response received";

      typeText(reply);
    } catch (err) {
      console.error("API ERROR:", err);

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Server error. Try again." },
      ]);

      setLoading(false);
    }
  };

  // IMAGE UPLOAD
  const uploadImage = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setMessages((prev) => [
      ...prev,
      { role: "user", text: "📷 Image uploaded" },
    ]);

    setLoading(true);

    try {
      const res = await axios.post(
        "https://helpershot.onrender.com/analyze",
        formData,
        { timeout: 120000 }
      );

      setLoading(false);

      const reply = res?.data?.ai || "No response";

      typeText(reply);
    } catch (err) {
      console.error("IMAGE ERROR:", err);

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Image processing failed." },
      ]);

      setLoading(false);
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        background: "#0b1220",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "white",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "850px",
          height: "95vh",
          display: "flex",
          flexDirection: "column",
          background: "#111827",
          borderRadius: "16px",
          overflow: "hidden",
        }}
      >
        {/* HEADER */}
        <div
          style={{
            padding: "15px",
            background: "linear-gradient(90deg,#1d4ed8,#2563eb)",
            textAlign: "center",
            fontWeight: "bold",
            fontSize: "18px",
          }}
        >
          🚀 HelperShot AI
        </div>

        {/* CHAT */}
        <div
          ref={chatRef}
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "20px",
          }}
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent:
                  msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  background:
                    msg.role === "user" ? "#2563eb" : "#1f2937",
                  padding: "12px 14px",
                  borderRadius: "14px",
                  margin: "8px",
                  maxWidth: "75%",
                }}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ padding: "10px", opacity: 0.6 }}>
              ⏳ Processing...
            </div>
          )}
        </div>

        {/* INPUT */}
        <div
          style={{
            display: "flex",
            padding: "12px",
            background: "#020617",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <input
            type="file"
            id="fileUpload"
            style={{ display: "none" }}
            onChange={(e) => uploadImage(e.target.files[0])}
          />

          <button
            onClick={() =>
              document.getElementById("fileUpload").click()
            }
            style={{
              padding: "10px",
              borderRadius: "10px",
              background: "#1e293b",
              border: "none",
              color: "white",
              cursor: "pointer",
            }}
          >
            📷
          </button>

          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            style={{
              flex: 1,
              padding: "12px",
              borderRadius: "12px",
              border: "none",
              background: "#111827",
              color: "white",
              outline: "none",
            }}
          />

          <button
            onClick={sendMessage}
            style={{
              padding: "12px",
              background: "#22c55e",
              border: "none",
              borderRadius: "12px",
              color: "white",
              cursor: "pointer",
            }}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}