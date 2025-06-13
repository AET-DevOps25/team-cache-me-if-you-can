import Navigator from "../../nav/Navigator";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useGroup } from "../home/components/GroupProvider";
import { useAuth } from "../../auth/AuthProvider";
import GroupInfo from "./components/GroupInfo";
import "./group_page.css";

export default function GroupPage() {
  const [activeTab, setActiveTab] = useState("Group Info");
  const { currentGroup } = useGroup();
  const [tabs, setTabs] = useState(["Group Info"]);
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (auth.user) {
      setTabs(["Group Info", "Materials", "Chats", "AI Bot"]);
    } else {
      setTabs(["Group Info"]);
    }
  }, [auth.user]);

  if (!currentGroup) {
    navigate("/");
  }

  return (
    currentGroup && (
      <>
        <Navigator />
        <div className="group-container">
          <div className="group-content">
            {/* Sidebar Navigation */}
            <div className="sidebar">
              <ul className="tab-list">
                {tabs.map((tab) => (
                  <li
                    key={tab}
                    className={`tab-item ${activeTab === tab ? "active" : ""}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab}
                  </li>
                ))}
              </ul>
            </div>

            {/* Content Area */}
            <div className="content-area">
              <h2 className="group-title">{currentGroup.name}</h2>
              <div className="tab-content">
                {activeTab === "Group Info" && <GroupInfo />}
                {activeTab === "Materials" && (
                  <p>Study materials for this group</p>
                )}
                {activeTab === "Chats" && <p>Chat history and messages</p>}
                {activeTab === "AI Bot" && (
                  <p>AI assistant for this study group</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </>
    )
  );
}
