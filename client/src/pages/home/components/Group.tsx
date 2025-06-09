import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./group.css";
import { Find } from "./Find";
import { Create } from "./Create";
import defaultImg from "../../../local_img/default.jpg";
import { useAuth } from "../../../auth/AuthProvider";
import { useGroup } from "./GroupProvider";
import { GroupData } from "../../../models/GroupData";

export default function Group() {
  const [groups, setGroups] = useState<Array<GroupData> | null>(null);
  const { setCurrentGroup } = useGroup();
  const auth = useAuth();
  const [activeView, setActiveView] = useState<"groups" | "create" | "search">(
    "groups"
  );
  const navigate = useNavigate();

  async function getAllGroups() {
    setGroups([
      {
        id: 1,
        name: "Biology 101",
        university: "TUM",
        description: "This is a group for Biology 101",
        imageUrl: defaultImg,
      },
      {
        id: 2,
        name: "Computer Science",
        university: "TUM",
        description: "This is a group for Computer Science",
        imageUrl: defaultImg,
      },
      {
        id: 3,
        name: "Psychology",
        university: "TUM",
        description: "This is a group for Psychology",
        imageUrl: defaultImg,
      },
    ]);
    //TODO: get all groups in no authentication info
  }

  async function getMyGroups() {
    setGroups([
      {
        id: 1,
        name: "Biology 101",
        university: "TUM",
        description: "This is a group for Biology 101",
        imageUrl: defaultImg,
      },
    ]);
    //TODO: get groups if user logged in
  }

  function clickGroup(id: number, group: GroupData) {
    navigate(`/group/${id}`);
    setCurrentGroup(group);
  }

  useEffect(() => {
    setCurrentGroup(null);
    if (auth.user) {
      getMyGroups();
    } else {
      getAllGroups();
    }
  }, [auth.user]);

  if (!groups && !auth.user) {
    return <p>Loding...</p>;
  }

  return (
    <div className="groups-container">
      {activeView === "groups" && <h2 className="groups-title">My Groups</h2>}

      {/* Action Buttons */}
      <div className="groups-actions">
        <button
          className="groups-button groups-button-margin"
          onClick={() =>
            setActiveView(activeView === "create" ? "groups" : "create")
          }
        >
          {activeView === "create" ? "back" : "create"}
        </button>

        <button
          className="groups-button"
          onClick={() =>
            setActiveView(activeView === "search" ? "groups" : "search")
          }
        >
          {activeView === "search" ? "back" : "search"}
        </button>
      </div>

      {/* Groups Container */}
      {activeView === "groups" ? (
        <div className="groups-img-container">
          {groups ? (
            groups.map((group) => (
              <div key={group.id} className="group-item">
                <div
                  className="group-image"
                  onClick={() => clickGroup(group.id, group)}
                >
                  <img src={group.imageUrl} alt="group image"></img>
                </div>
                <h3>{group.name}</h3>
              </div>
            ))
          ) : (
            <p>Join a Group!</p>
          )}
        </div>
      ) : activeView === "create" ? (
        <div className="groups-form">
          {/* Create Group Form */}
          <Create setActiveView={setActiveView} />
        </div>
      ) : (
        <div className="groups-form">
          {/* Find Groups Form */}
          <Find />
        </div>
      )}
    </div>
  );
}
