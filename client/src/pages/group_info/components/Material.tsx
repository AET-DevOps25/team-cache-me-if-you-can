import React, { useEffect, useState } from "react";
import "./material.css";

interface MaterialItem {
  id: string;
  name: string;
  url: string;
  uploadedAt: string;
}

const mockFetchMaterials = (): Promise<MaterialItem[]> => {
  return new Promise((resolve) =>
    setTimeout(() => {
      resolve([
        {
          id: "1",
          name: "Lecture_1_Notes.pdf",
          url: "#",
          uploadedAt: new Date().toLocaleDateString(),
        },
        {
          id: "2",
          name: "Project_Guidelines.docx",
          url: "#",
          uploadedAt: new Date().toLocaleDateString(),
        },
      ]);
    }, 1000)
  );
};

const mockUploadMaterial = (file: File): Promise<MaterialItem> => {
  return new Promise((resolve) =>
    setTimeout(() => {
      resolve({
        id: Date.now().toString(),
        name: file.name,
        url: "#",
        uploadedAt: new Date().toLocaleDateString(),
      });
    }, 1000)
  );
};

const Material: React.FC = () => {
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const loadMaterials = async () => {
      setLoading(true);
      const data = await mockFetchMaterials();
      setMaterials(data);
      setLoading(false);
    };

    loadMaterials();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const uploaded = await mockUploadMaterial(file);
    setMaterials((prev) => [...prev, uploaded]);
    setUploading(false);
    e.target.value = ""; // clear input for next upload
  };

  return (
    <div className="material-container">
      <div className="material-header">
        <label className="upload-button">
          {uploading ? "Uploading..." : "Upload Material"}
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            hidden
          />
        </label>
      </div>

      {loading ? (
        <p>Loading materials...</p>
      ) : materials.length === 0 ? (
        <p>No materials uploaded yet.</p>
      ) : (
        <ul className="material-list">
          {materials.map((mat) => (
            <li key={mat.id} className="material-item">
              <a href={mat.url} target="_blank" rel="noopener noreferrer">
                {mat.name}
              </a>
              <span className="upload-date">{mat.uploadedAt}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Material;
