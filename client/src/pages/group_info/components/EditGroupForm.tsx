import React, { useState, useEffect } from "react";
import { GroupData } from "../../../models/GroupData"; // Make sure path is correct
import { useAuth } from "../../../auth/AuthProvider"; // To get the token

interface EditGroupFormProps {
    group: GroupData;
    onUpdateSuccess: (updatedGroup: GroupData) => void;
    onCancel: () => void;
}

export function EditGroupForm({ group, onUpdateSuccess, onCancel }: EditGroupFormProps) {
    const [name, setName] = useState(group.name);
    const [university, setUniversity] = useState(group.university);
    const [description, setDescription] = useState(group.description);
    const [imageUrl, setImageUrl] = useState(group.imageUrl || "");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { token } = useAuth(); // Get the authentication token

    useEffect(() => {
        setName(group.name);
        setUniversity(group.university);
        setDescription(group.description);
        setImageUrl(group.imageUrl || "");
    }, [group]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        const updatedData = {
            name,
            university,
            description,
            imageUrl,
        };

        try {
            const res = await fetch(`/api/v1/groups/${group.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`, // Include the authorization token
                },
                body: JSON.stringify(updatedData),
            });

            if (!res.ok) {
                const errText = await res.text();
                throw new Error(errText || "Failed to update group");
            }

            const data: GroupData = await res.json();
            onUpdateSuccess(data); // Call success callback with updated group data
        } catch (err: any) {
            console.error("Error updating group:", err);
            setError(err.message || "An unexpected error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="edit-group-form-container">
            <h3>Edit Group Details</h3>
            <form onSubmit={handleSubmit} className="edit-group-form">
                <label>
                    Group Name:
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        maxLength={50}
                    />
                </label>
                <label>
                    University:
                    <input
                        type="text"
                        value={university}
                        onChange={(e) => setUniversity(e.target.value)}
                        required
                        maxLength={50}
                    />
                </label>
                <label>
                    Description:
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        maxLength={300}
                    />
                </label>
                <label>
                    Image URL:
                    <input
                        type="text"
                        value={imageUrl}
                        onChange={(e) => setImageUrl(e.target.value)}
                        placeholder="Optional image URL"
                    />
                </label>
                {error && <p className="error-message">{error}</p>}
                <div className="form-actions">
                    <button type="submit" disabled={loading}>
                        {loading ? "Saving..." : "Save Changes"}
                    </button>
                    <button type="button" onClick={onCancel} disabled={loading}>
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}