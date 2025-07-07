// src/components/group/components/GroupInfo.tsx
import { useState } from "react";
import { useGroup } from "../../home/components/GroupProvider";
import { useAuth } from "../../../auth/AuthProvider";
import { GroupData } from "../../../models/GroupData";
import { EditGroupForm } from "./EditGroupForm";
import defaultImg from "../../../local_img/default.jpg"; // Adjust path as needed

export function GroupInfo() {
    const { currentGroup, setCurrentGroup, refreshGroups } = useGroup();
    const { user,token } = useAuth(); // Get the authenticated username
    const [isEditing, setIsEditing] = useState(false);

    if (!currentGroup) {
        return <p>Select a group to see its info.</p>;
    }

    // Determine if the current authenticated user is the owner of this group
    const isOwner = user && currentGroup.ownerUsername === user;
    const isMember = user && currentGroup.memberUsernames.includes(user);

    // Handler to join
         const handleJoin = async () => {
           const res = await fetch(`/api/v1/groups/${currentGroup.id}/join`, {
                 method: "POST",
                 headers: {
                   "Content-Type": "application/json",
                       Authorization: `Bearer ${token}`,
                     },
           });
             if (!res.ok) return alert("Leave failed");
             await refreshGroups();
             const updated = await res.json();
             setCurrentGroup(updated);
         };

     // Handler to leave
         const handleLeave = async () => {
           const res = await fetch(`/api/v1/groups/${currentGroup.id}/leave`, {
                 method: "POST",
                 headers: {
                   "Content-Type": "application/json",
                       Authorization: `Bearer ${token}`,
                     },
           });
           if (!res.ok) return alert("Leave failed");
           const updated = await res.json();
           setCurrentGroup(updated);
           await refreshGroups();
         };
    const handleUpdateSuccess = (updatedGroup: GroupData) => {
        setCurrentGroup(updatedGroup); // Update the group in the context with the new data
        setIsEditing(false); // Exit editing mode
    };

    const handleCancelEdit = () => {
        setIsEditing(false); // Exit editing mode without saving changes
    };

    return (
        <div className="group-info-main-container">
            {isEditing ? (
                // Render the EditGroupForm when in editing mode
                <EditGroupForm
                    group={currentGroup}
                    onUpdateSuccess={handleUpdateSuccess}
                    onCancel={handleCancelEdit}
                />
            ) : (
                // Render the group details when not in editing mode
                <div className="group-details-view">
                    <h3 className="group-info-name">{currentGroup.name}</h3>
                    {currentGroup.imageUrl && (
                        <div className="group-info-image-wrapper">
                            <img
                                src={currentGroup.imageUrl || defaultImg} // Use defaultImg as fallback
                                alt={`${currentGroup.name} group image`}
                                className="group-info-image"
                            />
                        </div>
                    )}
                    <p>
                        <strong>University:</strong> {currentGroup.university}
                    </p>
                    <p>
                        <strong>Description:</strong> {currentGroup.description}
                    </p>
                    <p>
                        <strong>Owner:</strong> {currentGroup.ownerUsername}
                    </p>
                    {/* Display members list */}
                    {currentGroup.memberUsernames && currentGroup.memberUsernames.length > 0 && (
                        <div className="group-members-list">
                            <strong>Members:</strong>
                            <ul>
                                {Array.from(currentGroup.memberUsernames).map((member, index) => (
                                    <li key={index}>{member}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {/* JOIN/LEAVE buttons for non-owners */}
                    {user && !isOwner && (
                        <div>
                            {!isMember ? (
                                <button onClick={handleJoin} className="join-group-button">
                                    Join Group
                                </button>
                            ) : (
                                <button onClick={handleLeave} className="leave-group-button">
                                    Leave Group
                                </button>
                            )}
                        </div>
                    )}

                    {/* Only show the Edit button if the current user is the owner */}
                    {isOwner && (
                        <button onClick={() => setIsEditing(true)} className="edit-group-button">
                            Edit Group Details
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}