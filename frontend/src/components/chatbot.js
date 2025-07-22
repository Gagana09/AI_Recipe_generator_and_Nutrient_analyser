import React, { useState } from "react";
import "../styles/chatbot.css";

const Chatbot = ({ closeChatbot }) => {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleSendPrompt = () => {
    if (prompt) {
      // Example response logic (replace this with an API call if needed)
      setResponse(`You asked: "${prompt}". This is a placeholder response.`);
      setPrompt("");
    }
  };

  return (
    <div className="chatbot-popup">
      <div className="chatbot-header">
        <h3>AI Chatbot</h3>
        <button className="close-btn" onClick={closeChatbot}>
          ✖
        </button>
      </div>
      <div className="chatbot-body">
        <div className="chatbot-messages">
          {response && <p className="chatbot-response">{response}</p>}
        </div>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type your question..."
        />
        <button onClick={handleSendPrompt}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
