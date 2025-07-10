import { useEffect, useState, useRef } from "react";
import Navigator from "../../nav/Navigator";
import { useNavigate, useParams } from "react-router-dom";
import { useGroup } from "../home/components/GroupProvider";
import { useAuth } from "../../auth/AuthProvider";
import { GroupInfo } from "./components/GroupInfo";
import { Material } from "./Material";
import "./group_page.css";

export default function GroupPage() {
    const { groupId } = useParams<{ groupId: string }>();
    const { currentGroup, setCurrentGroup } = useGroup();
    const auth = useAuth();
    const navigate = useNavigate();
    const abortControllerRef = useRef<AbortController | null>(null);

    const [loadingGroup, setLoadingGroup] = useState(true);
    const [groupError, setGroupError] = useState<string | null>(null);

    const [tabs, setTabs] = useState<string[]>(["Group Info"]);
    const [activeTab, setActiveTab] = useState("Group Info");

    // Fetch group on mount / token change
    useEffect(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        abortControllerRef.current = new AbortController();

        setLoadingGroup(true);
        setGroupError(null);

        fetch(`/api/v1/groups/${groupId}`, {
            headers: {
                "Content-Type": "application/json",
                ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
            },
            signal: abortControllerRef.current.signal,
        })
            .then((res) => {
                if (!res.ok) {
                    if (res.status === 404) {
                        throw new Error("Group not found");
                    } else if (res.status === 403) {
                        throw new Error("Access denied");
                    } else if (res.status >= 500) {
                        throw new Error("Server error - please try again");
                    } else {
                        throw new Error("Failed to fetch group");
                    }
                }
                return res.json();
            })
            .then((data) => {
                setCurrentGroup(data);
                setLoadingGroup(false);
            })
            .catch((err: any) => {
                if (err.name === 'AbortError') {
                    return;
                }

                setGroupError(err.message);
                setLoadingGroup(false);

                if (err.message.includes("not found") || err.message.includes("Access denied")) {
                    navigate("/", { replace: true });
                }
            });

        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [groupId, auth.token, setCurrentGroup, navigate]);

    // Helper function to check access - corrected to use memberUsernames
    const hasAccess = () => {
        if (!auth.user || !currentGroup) return false;

        // Check if user is owner
        const isOwner = currentGroup.ownerUsername === auth.user;

        // Check if user is member - use memberUsernames array/set
        const isMember = currentGroup.memberUsernames &&
            currentGroup.memberUsernames.includes(auth.user);

        return isOwner || isMember;
    };

    // Rebuild tabs whenever user or group changes
    useEffect(() => {
        const base = ["Group Info"];
        if (hasAccess()) {
            base.push("Materials", "Chats", "AI Bot");
        }
        setTabs(base);

        if (!base.includes(activeTab) && activeTab !== "Group Info") {
            setActiveTab("Group Info");
        }
    }, [auth.user, currentGroup, activeTab]);

    if (loadingGroup) {
        return (
            <>
                <Navigator />
                <div className="group-container">
                    <p>Loading group details…</p>
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
                    <button onClick={() => window.location.reload()}>
                        Retry
                    </button>
                </div>
            </>
        );
    }

    if (!currentGroup) {
        return (
            <>
                <Navigator />
                <div className="group-container">
                    <p>No group found.</p>
                </div>
            </>
        );
    }

    return (
        <>
            <Navigator />
            <div className="group-container">
                <div className="group-content">
                    <aside className="sidebar">
                        <ul className="tab-list">
                            {tabs.map((tab) => (
                                <li
                                    key={tab}
                                    className={`tab-item ${
                                        tab === activeTab ? "active" : ""
                                    }`}
                                    onClick={() => setActiveTab(tab)}
                                >
                                    {tab}
                                </li>
                            ))}
                        </ul>
                    </aside>

                    <section className="content-area">
                        <h2 className="group-title">{currentGroup?.name || "Unknown Group"}</h2>

                        {activeTab === "Group Info" && <GroupInfo />}

                        {activeTab === "Materials" && (
                            hasAccess() ? (
                                <Material />
                            ) : (
                                <p className="access-message">
                                    You must be a member (or owner) to view Materials.
                                </p>
                            )
                        )}

                        {activeTab === "Chats" && (
                            hasAccess() ? (
                                <p>(Your Chats UI…)</p>
                            ) : (
                                <p className="access-message">
                                    You must be a member (or owner) to access Chats.
                                </p>
                            )
                        )}

                        {activeTab === "AI Bot" && (
                            hasAccess() ? (
                                <p>(Your AI Bot UI…)</p>
                            ) : (
                                <p className="access-message">
                                    You must be a member (or owner) to access the AI Bot.
                                </p>
                            )
                        )}
                    </section>
                </div>
            </div>
        </>
    );
}