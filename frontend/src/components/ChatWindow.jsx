import { useState, useRef } from "react";

const hasSpeech =
  typeof window !== "undefined" &&
  ("webkitSpeechRecognition" in window || "SpeechRecognition" in window);

const SpeechRecognition =
  typeof window !== "undefined"
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null;

export default function ChatWindow({ messages, onSendMessage, disabled, language }) {
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const recRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSendMessage(input);
    setInput("");
  };

  const startListening = () => {
    if (!SpeechRecognition) return;
    const rec = new SpeechRecognition();
    recRef.current = rec;
    rec.lang =
      language === "es" ? "es-ES" : language === "bn" ? "bn-BD" : "en-US";
    rec.interimResults = false;
    rec.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + text : text));
    };
    rec.onend = () => setListening(false);
    rec.start();
    setListening(true);
  };

  const stopListening = () => {
    recRef.current?.stop();
    setListening(false);
  };

  const handleVoiceClick = () => {
    if (!hasSpeech) {
      alert("Voice input is not supported in this browser.");
      return;
    }
    if (listening) stopListening();
    else startListening();
  };

  return (
    <div className="chat-card">
      <div className="chat-messages" aria-label="Chat history">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={
              m.role === "assistant" ? "chat-bubble assistant" : "chat-bubble user"
            }
          >
            {m.content}
          </div>
        ))}
      </div>

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <button
          type="button"
          className={`voice-btn ${listening ? "voice-active" : ""}`}
          onClick={handleVoiceClick}
        >
          🎤
        </button>
        <input
          className="chat-input"
          placeholder="Enter your goal / prompts here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" className="send-btn" disabled={disabled}>
          ➤
        </button>
      </form>
    </div>
  );
}
