// src/pages/home/components/Group.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./group.css";
import { Find } from "./Find";
import { Create } from "./Create";
import defaultImg from "../../../local_img/default.jpg";
import { useAuth } from "../../../auth/AuthProvider";
import { useGroup } from "./GroupProvider";
import { GroupData } from "../../../models/GroupData"; // Make sure to import GroupData

export default function Group() {
  const { setCurrentGroup, groups, refreshGroups } = useGroup();
  const auth = useAuth();
  const [activeView, setActiveView] = useState<"groups" | "create" | "search">(
      "groups"
  );
  // New state to control if "All Groups" are being shown or "My Groups"
  const [showAllGroups, setShowAllGroups] = useState(false);

  const navigate = useNavigate();

  function clickGroup(id: number, group: GroupData) {
    navigate(`/group/${id}`);
    setCurrentGroup(group);
  }

  useEffect(() => {
    setCurrentGroup(null);
    // Refresh groups whenever the user changes or activeView changes to 'groups'
    if (activeView === "groups") {
      refreshGroups();
    }
  }, [auth.user, setCurrentGroup, activeView, refreshGroups]); // Added refreshGroups to dependencies

  // Filter groups for "My Groups" display
  const myGroups = groups
      ? groups.filter(
          (g) =>
              auth.user &&
              (g.ownerUsername === auth.user ||
                  (g.memberUsernames && g.memberUsernames.includes(auth.user)))
      )
      : [];

  const displayedGroups = auth.user && !showAllGroups ? myGroups : groups;

  if (!groups && activeView === "groups") {
    return <p>Loading groups...</p>;
  }

  return (
      <div className="groups-container">
        {activeView === "groups" && (
            <h2 className="groups-title">
              {auth.user && !showAllGroups ? "My Groups" : "All Groups"}
            </h2>
        )}

        <div className="groups-actions">
          {auth.user && (
              <button
                  className="groups-button groups-button-margin"
                  onClick={() => {
                    setActiveView(activeView === "create" ? "groups" : "create");
                    // Reset showAllGroups when switching to create view
                    setShowAllGroups(false);
                  }}
              >
                {activeView === "create" ? "Back to My Groups" : "Create Group"}
              </button>
          )}

          <button
              className="groups-button"
              onClick={() => {
                setActiveView(activeView === "search" ? "groups" : "search");
                // Reset showAllGroups when switching to search view
                setShowAllGroups(false);
              }}
          >
            {activeView === "search"
                ? "Back to " + (auth.user && !showAllGroups ? "My Groups" : "All Groups")
                : "Search Groups"}
          </button>

          {auth.user && activeView === "groups" && (
              <button
                  className="groups-button"
                  onClick={() => setShowAllGroups(!showAllGroups)} // Toggle showAllGroups
              >
                {showAllGroups ? "View My Groups" : "View All Groups"}
              </button>
          )}
        </div>

        {activeView === "groups" ? (
            <div className="groups-img-container">
              {displayedGroups && displayedGroups.length > 0 ? (
                  displayedGroups.map((group) => (
                      <div key={group.id} className="group-item">
                        <div
                            className="group-image"
                            onClick={() => clickGroup(group.id, group)}
                        >
                          <img
                              src={group.imageUrl || defaultImg}
                              alt={`${group.name} image`}
                          />
                        </div>
                        <h3>{group.name}</h3>
                        {group.ownerUsername && (
                            <p className="group-owner">
                              Owner: {group.ownerUsername}
                            </p>
                        )}
                        {auth.user && group.isMember && (
                            <p className="group-member-status">✅ Member</p>
                        )}
                      </div>
                  ))
              ) : (
                  <p>
                    {auth.user && !showAllGroups
                        ? "You haven't joined or created any groups yet."
                        : "No groups available. Please create one or check back later!"}
                  </p>
              )}
            </div>
        ) : activeView === "create" ? (
            <div className="groups-form">
              <Create setActiveView={setActiveView} />
            </div>
        ) : (
            <div className="groups-form">
              <Find />
            </div>
        )}
      </div>
  );
}