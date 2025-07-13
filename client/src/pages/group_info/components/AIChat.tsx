import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import "./ai_chat.css";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

const AIChat: React.FC = () => {
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

  const simulateServerResponse = async (
    userMessage: string
  ): Promise<string> => {
    console.log(userMessage);
    await new Promise((resolve) =>
      setTimeout(resolve, 1000 + Math.random() * 2000)
    );

    const responses = [
      "That's interesting! Tell me more.",
      "I understand what you're saying.",
      "Thanks for sharing that with me.",
      "I see your point. What do you think about it?",
      "That's a great question. Let me think about it.",
      "I appreciate you bringing this up.",
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsThinking(true);

    try {
      const response = await simulateServerResponse(inputText);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I encountered an error. Please try again.",
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
