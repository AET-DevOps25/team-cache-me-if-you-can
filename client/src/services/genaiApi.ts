const BASE_URL = "/api/v1";

export const uploadDocumentForGenai = async (
    groupId: string,
    file: File,
    token: string
): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/groups/${groupId}/documents`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to upload document");
    }

    return response.json();
};

export const queryGenai = async (
    groupId: string,
    question: string,
    token: string
): Promise<any> => {
    const response = await fetch(`${BASE_URL}/groups/${groupId}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to send message");
    }

    return response.json();
}; 