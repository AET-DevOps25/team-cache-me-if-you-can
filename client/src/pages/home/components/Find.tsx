import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../../auth/AuthProvider"; // Import useAuth
import defaultImg from "../../../local_img/default.jpg";
import "./find.css";

export function Find() {
  const navigate = useNavigate();
  const auth = useAuth();
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [groups, setGroups] = useState<
    | {
        id: number;
        name: string;
        description: string;
        university: string;
        imageUrl: string | null;
        memberUsernames: string[];
      }[]
    | null
  >(null);

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return alert("Please enter text to search");

    setIsSearching(true);
    try {
      const res = await fetch(
        `/api/v1/groups/search?query=${encodeURIComponent(query)}`,
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || res.statusText);
      }

      const data = await res.json();
      setGroups(data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error("Search failed:", err);
      alert("Search error: " + err.message);
      setGroups([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="find-container">
      <form className="find-groups-form" onSubmit={handleSearchSubmit}>
        <input
          type="text"
          placeholder="Search by name or university"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={isSearching || !query.trim()}>
          {isSearching ? "Searching…" : "Search"}
        </button>
      </form>

      {groups === null ? null : groups.length > 0 ? (
        <div className="groups-img-container">
          {groups.map((g) => (
            <div
              key={g.id}
              className="group-item"
              onClick={() => navigate(`/group/${g.id}`)}
            >
              <img
                src={g.imageUrl || defaultImg}
                alt={g.name}
                className="group-image"
              />
              <h3>{g.name}</h3>
              <p>{g.university}</p>
              {/* Check membership */}
              {auth.user &&
                g.memberUsernames &&
                Array.from(g.memberUsernames).includes(auth.user) && (
                  <span>✅ Joined</span>
                )}
            </div>
          ))}
        </div>
      ) : (
        <p>No Groups Found.</p>
      )}
    </div>
  );
}
