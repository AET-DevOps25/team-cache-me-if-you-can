import Navigator from "../../nav/Navigator";
import { useParams } from "react-router-dom";
import { useState } from "react";
import "./group_info.css";
import AIChat from "./components/AIChat";
import Material from "./components/Material";

export default function GroupInfo() {
  const { groupName } = useParams();
  const [activeTab, setActiveTab] = useState("Group Name");

  const tabs = ["Group Info", "Materials", "Chats", "AI Bot"];
  return (
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
            <h2 className="group-title">{groupName}</h2>
            <div className="tab-content">
              {activeTab === "Group Name" && (
                <p>Group information and settings for {groupName}</p>
              )}
              {activeTab === "Materials" && <Material />}
              {activeTab === "Chats" && <p>Chat history and messages</p>}
              {activeTab === "AI Bot" && <AIChat />}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
