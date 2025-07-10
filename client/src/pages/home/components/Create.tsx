import { useState } from "react";
import { useAuth } from "../../../auth/AuthProvider"; // Import useAuth
import "./create.css";
import defaultImg from "../../../local_img/default.jpg";
import {useNavigate} from "react-router-dom";

interface CreateGroupFormData {
  name: string;
  university: string;
  description: string;
  imageUrl: string | null;
}

export function Create({
                         setActiveView,
                       }: {
  setActiveView: (view: "groups" | "create" | "search") => void;
}) {
  const [isCreating, setIsCreating] = useState(false);
  const auth = useAuth(); // includes the token
  const navigate = useNavigate();
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
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      // Add Authorization header if a token exists
      if (auth.token) {
        headers["Authorization"] = `Bearer ${auth.token}`;
      } else {
        // Handle case where token is missing (e.g., user not logged in or session expired)
        alert("You must be logged in to create a group.");
        setIsCreating(false);
        navigate('/login');
        return;
      }

      const response = await fetch("/api/v1/groups", {
        method: "POST",
        headers: headers, // Use the dynamically created headers object
        body: JSON.stringify(createFormData),
      });

      if (!response.ok) {
        let errorMessage = "Failed to create group. Please try again.";
        try {
          const errorData = await response.json();
          // Attempt to get a more specific message if available from backend
          errorMessage = errorData.message || errorData.error || errorMessage;
        } catch (jsonError) {
          // If response is not JSON or parsing fails, use generic message
          console.error("Error parsing error response:", jsonError);
        }
        throw new Error(errorMessage);
      }

      const newGroupResponse = await response.json();
      console.log("Group created:", newGroupResponse);

      // Reset form
      setCreateFormData({
        name: "",
        university: "",
        description: "",
        imageUrl: defaultImg,
      });

      // Navigate back to groups view
      setActiveView("groups");
    } catch (error: any) {
      console.error("Error creating group:", error);
      alert("Error: " + error.message);
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
          {/* Group Name Input */}
          <div className="form-group">
            <label htmlFor="name">Group Name</label>
            <input
                type="text"
                id="name"
                name="name"
                placeholder="Enter group name"
                value={createFormData.name}
                onChange={handleInputChange}
                className="form-input"
                maxLength={50}
                required
            />
          </div>

          {/* University Input */}
          <div className="form-group">
            <label htmlFor="university">University</label>
            <input
                type="text"
                id="university"
                name="university"
                placeholder="Enter university name"
                value={createFormData.university}
                onChange={handleInputChange}
                className="form-input"
                maxLength={50}
                required
            />
          </div>

          {/* Description Input */}
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
                id="description"
                name="description"
                placeholder="Enter group description"
                value={createFormData.description}
                onChange={handleInputChange}
                className="form-input"
                rows={4}
                maxLength={300}
            />
          </div>

          {/* Group Image URL Input */}
          <div className="form-group">
            <label htmlFor="imageUrl">Group Image URL</label>
            <input
                type="text"
                id="imageUrl"
                name="imageUrl"
                placeholder="Enter image URL (e.g., from your files service)"
                value={createFormData.imageUrl || ""}
                onChange={handleInputChange}
                className="form-input"
                maxLength={500}
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