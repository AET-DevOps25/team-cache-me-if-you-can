const BASE_URL = "/api/v1";

// Types for handwritten documents
export interface HandwrittenDocument {
    task_id: string;
    original_filename: string;
    processed_filename?: string;
    status: "PENDING" | "SUCCESS" | "FAILURE";
    upload_timestamp: string;
    group_id: string;
    error_message?: string;
}

export interface HandwrittenListResponse {
    processing: HandwrittenDocument[];
    completed: HandwrittenDocument[];
}

export interface HandwrittenUploadResponse {
    task_id: string;
    filename: string;
    message: string;
    error?: string;
}

export interface HandwrittenStatusResponse {
    task_id: string;
    status: string;
    original_filename: string;
    processed_filename?: string;
    error_message?: string;
}

// Upload handwritten document for processing
export const uploadHandwrittenDocument = async (
    groupId: string,
    file: File,
    token: string
): Promise<HandwrittenUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/handwritten/upload`, {
        method: "POST",
        headers: {
            "X-Group-ID": groupId,
            Authorization: `Bearer ${token}`,
        },
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to upload handwritten document");
    }

    return response.json();
};

// List handwritten documents for a group
export const listHandwrittenDocuments = async (
    groupId: string,
    token: string
): Promise<HandwrittenListResponse> => {
    try {
        const response = await fetch(`${BASE_URL}/handwritten/`, {
            method: "GET",
            headers: {
                "X-Group-ID": groupId,
                Authorization: `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    } catch (error: any) {
        console.error(`List handwritten documents failed: ${error.message}`);
        // Return empty lists as fallback
        return { processing: [], completed: [] };
    }
};

// Get handwritten document status
export const getHandwrittenStatus = async (
    taskId: string,
    token: string
): Promise<HandwrittenStatusResponse> => {
    const response = await fetch(`${BASE_URL}/handwritten/${taskId}/status`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to get document status");
    }

    return response.json();
};

// Download processed document
export const downloadProcessedDocument = async (
    taskId: string,
    groupId: string,
    token: string,
    filename: string
): Promise<void> => {
    const response = await fetch(`${BASE_URL}/handwritten/${taskId}/download`, {
        method: "GET",
        headers: {
            "X-Group-ID": groupId,
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to download processed document");
    }

    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
};

// Delete handwritten document
export const deleteHandwrittenDocument = async (
    taskId: string,
    token: string
): Promise<any> => {
    const response = await fetch(`${BASE_URL}/handwritten/${taskId}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "An unknown error occurred" }));
        throw new Error(errorData.message || "Failed to delete handwritten document");
    }

    return response.json();
}; 