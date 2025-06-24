import { useState } from "react";
import { useNavigate } from "react-router-dom";
import defaultImg from "../../../local_img/default.jpg";
import "./find.css";

export function Find() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [groups, setGroups] = useState<Array<{
    id: number;
    name: string;
    imageUrl: string;
  }> | null>(null);

  async function getSearchedGroups(query: string) {
    setGroups([{ id: 1, name: query, imageUrl: defaultImg }]);
    //TODO: Implement actual API call to get all groups contains this query
  }

  const handleSearchSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();

    if (!query.trim()) {
      alert("Please enter a group name or university");
      return;
    }

    setIsSearching(true);

    try {
      // Simulate API call
      await getSearchedGroups(query);
      console.log("Group found:", groups);
    } catch (error) {
      console.error("Error searching group:", error);
      alert("Failed to find group. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="find-container">
      <div className="find-groups-form">
        {/* Find Groups Form */}
        <form onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="Search Groups with Group Names or University"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            className="find-form-submit-btn"
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
        </form>
      </div>
      <div className="groups-img-container">
        {groups ? (
          groups.map((group) => (
            <div key={group.id} className="group-item">
              <div
                className="group-image"
                onClick={() => navigate(`/group/${group.name}`)}
              >
                <img src={group.imageUrl} alt="group image"></img>
              </div>
              <h3>{group.name}</h3>
            </div>
          ))
        ) : (
          <p>No Group Found.</p>
        )}
      </div>
    </div>
  );
}
