import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./group.css";
import { Find } from "./Find";
import { Create } from "./Create";
import defaultImg from "../../../local_img/default.jpg";

export default function Group() {
  const [groups, setGroups] = useState<Array<{
    id: number;
    name: string;
    imageUrl: string;
  }> | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<"groups" | "create" | "find">(
    "groups"
  );
  const navigate = useNavigate();

  async function getAllGroups() {
    setGroups([
      { id: 1, name: "Biology 101", imageUrl: defaultImg },
      { id: 2, name: "Computer Science", imageUrl: defaultImg },
      { id: 3, name: "Psychology", imageUrl: defaultImg },
    ]);
    //TODO: get all groups in no authentication info
  }

  async function getMyGroups() {
    setGroups([{ id: 1, name: "Biology 101", imageUrl: defaultImg }]);
    //TODO: get groups if user logged in
  }

  async function getUserName() {
    //TODO: get authentication info
    setUserName(null);
  }

  useEffect(() => {
    const fetchData = async () => {
      await getUserName();

      if (userName) {
        await getMyGroups();
      } else {
        await getAllGroups();
      }
    };

    fetchData();
  }, [userName]);

  if (!groups && !userName) {
    return <p>Loding...</p>;
  }

  return (
    <div className="groups-container">
      <h2 className="groups-title">My Groups</h2>

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
            setActiveView(activeView === "find" ? "groups" : "find")
          }
        >
          {activeView === "find" ? "back" : "find"}
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
                  onClick={() => navigate(`/group/${group.name}`)}
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
          <Create setActiveView={setActiveView} setGroups={setGroups} />
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
