import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../../../auth/AuthProvider";
import { ChatMessage, getGroupChatMessages, sendChatMessage, deleteGroupChat } from "../../../services/groupApi";
import { useGroup } from "../../home/components/GroupProvider";
import "./group_chat.css";

export const Chat = () => {
    const { groupId } = useParams<{ groupId: string }>();
    const { user, token } = useAuth();
    const { currentGroup } = useGroup();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [newMessage, setNewMessage] = useState("");
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (groupId && token) {
            getGroupChatMessages(groupId, token)
                .then(setMessages)
                .catch(() => setError("Failed to load messages."));
        }
    }, [groupId, token]);

    useEffect(scrollToBottom, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim() || !groupId || !token) return;

        try {
            const sentMessage = await sendChatMessage(groupId, newMessage, token);
            setMessages([...messages, sentMessage]);
            setNewMessage("");
        } catch {
            setError("Failed to send message.");
        }
    };

    const handleDeleteChat = async () => {
        if (!groupId || !token) return;

        if (window.confirm("Are you sure you want to delete the entire chat history for this group? This cannot be undone.")) {
            try {
                await deleteGroupChat(groupId, token);
                setMessages([]);
            } catch {
                setError("Failed to delete chat.");
            }
        }
    };

    return (
        <div className="chat-container">
            <h3>Group Chat</h3>
            {error && <p className="error-message">{error}</p>}
            <div className="messages-list">
                {messages.map((msg) => (
                    <div key={msg.id} className={`message-item ${msg.username === user ? "sent" : "received"}`}>
                        <div className="message-content">
                            <strong>{msg.username}</strong>
                            <p>{msg.content}</p>
                            <span className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className="message-form">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                />
                <button type="submit">Send</button>
            </form>
            {currentGroup?.ownerUsername === user && (
                <button onClick={handleDeleteChat} className="delete-chat-btn">
                    Delete Chat History
                </button>
            )}
        </div>
    );
};
