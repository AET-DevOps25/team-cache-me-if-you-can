// src/pages/group_info/GroupPage.tsx
import Navigator from "../../nav/Navigator";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useGroup } from "../home/components/GroupProvider";
import { useAuth } from "../../auth/AuthProvider";
import { GroupInfo } from "./components/GroupInfo";
import "./group_page.css";
import { GroupData } from "../../models/GroupData";
import AIChat from "./components/AIChat";
import Material from "./components/Material";

export default function GroupPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { currentGroup, setCurrentGroup } = useGroup(); // refreshGroups is removed from destructuring here as it's not needed for this specific component
  const [activeTab, setActiveTab] = useState("Group Info");
  const [tabs, setTabs] = useState(["Group Info"]);
  const auth = useAuth();
  const navigate = useNavigate();
  const [loadingGroup, setLoadingGroup] = useState(true);
  const [groupError, setGroupError] = useState<string | null>(null);

  useEffect(() => {
    if (currentGroup && currentGroup.id === Number(groupId)) {
      setLoadingGroup(false);
      return;
    }

    const fetchGroupById = async () => {
      setLoadingGroup(true);
      setGroupError(null);
      try {
        const res = await fetch(`/api/v1/groups/${groupId}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
          },
        });

        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(errorText || "Failed to fetch group details.");
        }

        const data: GroupData = await res.json();
        setCurrentGroup(data);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        console.error("Error fetching group:", err);
        setGroupError(err.message || "Could not load group.");
        navigate("/", { replace: true });
      } finally {
        setLoadingGroup(false);
      }
    };

    fetchGroupById();
  }, [groupId, currentGroup, setCurrentGroup, navigate, auth.token]); // 'refreshGroups' is removed from these dependencies

  useEffect(() => {
    if (auth.user) {
      setTabs(["Group Info", "Materials", "Chats", "AI Bot"]);
    } else {
      setTabs(["Group Info"]);
    }
  }, [auth.user]);

  if (loadingGroup) {
    return (
      <>
        <Navigator />
        <div className="group-container">
          <p>Loading group details...</p>
        </div>
      </>
    );
  }

  if (groupError) {
    return (
      <>
        <Navigator />
        <div className="group-container">
          <p className="error-message">{groupError}</p>
        </div>
      </>
    );
  }

  if (!currentGroup) {
    return (
      <>
        <Navigator />
        <div className="group-container">
          <p>No group selected or found.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigator />
      <div className="group-container">
        <div className="group-content">
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

          <div className="content-area">
            <h2 className="group-title">{currentGroup.name}</h2>
            <div className="tab-content">
              {activeTab === "Group Info" && <GroupInfo />}
              {activeTab === "Materials" && <Material />}
              {activeTab === "Chats" && <p>Group Chat</p>}
              {activeTab === "AI Bot" && <AIChat />}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
