import { useState } from "react";
import "./create.css";
import defaultImg from "../../../local_img/default.jpg"; // Still useful for default image if URL is empty

interface CreateGroupFormData {
  name: string;
  university: string;
  description: string;
  imageUrl: string | null; // This is now a string URL
}

export function Create({
                         setActiveView,
                       }: {
  setActiveView: (view: "groups" | "create" | "search") => void;
}) {
  const [isCreating, setIsCreating] = useState(false);
  const [createFormData, setCreateFormData] = useState<CreateGroupFormData>({
    name: "",
    university: "",
    description: "",
    imageUrl: defaultImg, // Set a default image URL initially
  });

  const handleCreateSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!createFormData.name.trim()) {
      alert("Please enter a group name");
      return;
    }
    if (!createFormData.university.trim()) {
      alert("Please enter a university");
      return;
    }

    setIsCreating(true);

    try {
      // TODO: Implement actual API call to create group
      const response = await fetch("/api/v1/groups", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // You will need to add Authorization header if group creation is protected
          // "Authorization": `Bearer ${yourAuthToken}`
        },
        body: JSON.stringify(createFormData), // Send JSON directly
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create group");
      }

      const newGroupResponse = await response.json();
      console.log("Group created:", newGroupResponse);

      // Reset form
      setCreateFormData({
        name: "",
        university: "",
        description: "",
        imageUrl: defaultImg, // Reset to default
      });

      // Navigate back to groups view
      setActiveView("groups");
    } catch (error: any) {
      console.error("Error creating group:", error);
      alert("Failed to create group: " + error.message);
    } finally {
      setIsCreating(false);
    }
  };

  const handleInputChange = (
      e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setCreateFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
      <div className="groups-form">
        <form className="create-group-form" onSubmit={handleCreateSubmit}>
          {/* ... (existing name, university, description inputs) ... */}

          <div className="form-group">
            <label htmlFor="imageUrl">Group Image URL</label>
            <input
                type="text" // Changed to type="text"
                id="imageUrl"
                name="imageUrl"
                placeholder="Enter image URL (e.g., from your files service)"
                value={createFormData.imageUrl || ''} // Handle null value gracefully
                onChange={handleInputChange}
                className="form-input"
                maxLength={500} // A reasonable max length for a URL
            />
            {createFormData.imageUrl && (
                <div className="image-preview">
                  <img src={createFormData.imageUrl} alt="Preview" />
                </div>
            )}
          </div>

          <button
              type="submit"
              className="form-submit-btn"
              disabled={
                  isCreating ||
                  !createFormData.name.trim() ||
                  !createFormData.university.trim()
              }
          >
            {isCreating ? "Creating..." : "Create Group"}
          </button>
        </form>
      </div>
  );
}