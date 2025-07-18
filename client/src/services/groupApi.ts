const BASE_URL = "/api/v1/groups";

export interface ChatMessage {
  id: number;
  username: string;
  content: string;
  timestamp: string;
}

export const getGroupChatMessages = async (
  groupId: string,
  token: string
): Promise<ChatMessage[]> => {
  const response = await fetch(`${BASE_URL}/${groupId}/messages`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
    throw new Error(errorData.message || "Failed to fetch messages");
  }

  return response.json();
};

export const sendChatMessage = async (
  groupId: string,
  content: string,
  token: string
): Promise<ChatMessage> => {
  const response = await fetch(`${BASE_URL}/${groupId}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
    throw new Error(errorData.message || "Failed to send message");
  }

  return response.json();
};

export const deleteGroupChat = async (
  groupId: string,
  token: string
): Promise<void> => {
  const response = await fetch(`${BASE_URL}/${groupId}/messages`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
    throw new Error(errorData.message || "Failed to delete chat");
  }
}; 