import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import "./ai_chat.css";
import { useParams } from "react-router-dom";
import { useAuth } from "../../../auth/AuthProvider";
import { queryGenai } from "../../../services/genaiApi";
import { message as antdMessage } from 'antd';

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

const AIChat: React.FC = () => {
  const { groupId } = useParams<{ groupId: string }>();
  const auth = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || !groupId || !auth.token) {
        if (!groupId) antdMessage.error("Group ID is missing.");
        if (!auth.token) antdMessage.error("Authentication token is missing.");
        return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputText;
    setInputText("");
    setIsThinking(true);

    try {
      const response = await queryGenai(groupId, currentInput, auth.token);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: error.message || "Sorry, I encountered an error. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="ai-chat-wrapper">
      {/* Chat header (optional) */}
      <div className="chat-header">
        <h2 className="chat-title">AI Assistant</h2>
      </div>

      {/* Chat messages area */}
      <div className="chat-messages" id="chat-scroll">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-row ${msg.sender === "user" ? "user" : "bot"}`}
          >
            {msg.sender === "bot" && (
              <div className="avatar bot-avatar">
                <Bot className="icon" />
              </div>
            )}

            <div className={`message-bubble ${msg.sender}`}>{msg.text}</div>

            {msg.sender === "user" && (
              <div className="avatar user-avatar">
                <User className="icon" />
              </div>
            )}
          </div>
        ))}

        {isThinking && (
          <div className="message-row bot">
            <div className="avatar bot-avatar">
              <Bot className="icon" />
            </div>
            <div className="message-bubble bot thinking">
              Thinking<span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isThinking}
          className="chat-input"
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputText.trim() || isThinking}
          className="chat-send-btn"
        >
          <Send className="icon" />
        </button>
      </div>
    </div>
  );
};

export default AIChat;
