import { useState } from "react";
import "./create.css";
import defaultImg from "../../../local_img/default.jpg";

interface GroupData {
  id: number;
  name: string;
  imageUrl: string;
}
interface CreateGroupFormData {
  name: string;
  university: string;
  description: string;
  image: File | null;
}

export function Create({
  setActiveView,
  setGroups,
}: {
  setActiveView: (view: "groups" | "create" | "search") => void;
  setGroups: React.Dispatch<React.SetStateAction<GroupData[] | null>>;
}) {
  const [isCreating, setIsCreating] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [createFormData, setCreateFormData] = useState<CreateGroupFormData>({
    name: "",
    university: "",
    description: "",
    image: null,
  });

  const handleCreateSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!createFormData.name.trim()) {
      alert("Please enter a group name");
      return;
    }

    setIsCreating(true);

    try {
      // TODO: Implement actual API call to create group
      const newGroup: GroupData = {
        id: Date.now(), // Temporary ID generation
        name: createFormData.name.trim(),
        imageUrl: imagePreview || defaultImg,
      };

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Add new group to the list
      setGroups((prev) => (prev ? [newGroup, ...prev] : [newGroup]));
      // Reset form
      setCreateFormData({
        name: "",
        university: "",
        description: "",
        image: null,
      });
      setImagePreview(null);

      // Navigate back to groups view
      setActiveView("groups");

      console.log("Group created:", newGroup);
    } catch (error) {
      console.error("Error creating group:", error);
      alert("Failed to create group. Please try again.");
    } finally {
      setIsCreating(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCreateFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setCreateFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setCreateFormData((prev) => ({
      ...prev,
      image: file,
    }));
  };

  return (
    <div className="groups-form">
      {/* Create Group Form */}
      <form className="create-group-form" onSubmit={handleCreateSubmit}>
        <div className="form-group">
          <label htmlFor="groupName">Group Name</label>
          <input
            type="text"
            id="groupName"
            name="name"
            placeholder="Enter group name"
            value={createFormData.name}
            onChange={handleInputChange}
            className="form-input"
            required
            maxLength={50}
          />
        </div>

        <div className="form-group">
          <label htmlFor="university">University</label>
          <input
            type="text"
            id="university"
            name="university"
            placeholder="Enter the University"
            value={createFormData.university}
            onChange={handleInputChange}
            className="form-input"
            required
            maxLength={50}
          />
        </div>

        <div className="form-group">
          <label htmlFor="groupDescription">Description</label>
          <textarea
            id="groupDescription"
            name="description"
            placeholder="Enter group description (optional)"
            value={createFormData.description}
            onChange={handleTextareaChange}
            className="form-textarea"
            maxLength={300}
            rows={4}
          />
          <div className="character-count">
            {createFormData.description.length}/300 characters
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="groupImage">Group Image</label>
          <input
            type="file"
            id="groupImage"
            accept="image/*"
            onChange={handleImageChange}
            className="form-input-file"
          />

          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Preview" />
              <button
                type="button"
                onClick={() => {
                  setImagePreview(null);
                  setCreateFormData((prev) => ({ ...prev, image: null }));
                }}
                className="remove-image-btn"
              >
                Remove
              </button>
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
