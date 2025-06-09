import { useAuth } from "../../../auth/AuthProvider";
import { useGroup } from "../../home/components/GroupProvider";
export default function GroupInfo() {
  const { currentGroup } = useGroup();
  const auth = useAuth();

  return (
    currentGroup && (
      <div>
        <p
          style={{
            fontSize: "18px",
            fontWeight: "600",
            color: "#333",
            margin: "0 0 8px 0",
          }}
        >
          University: {currentGroup.university}
        </p>
        <p
          style={{
            color: "#666",
            lineHeight: "1.5",
            margin: "0 0 16px 0",
          }}
        >
          Description: {currentGroup.description}
        </p>
        {!auth.user && (
          <button
            style={{
              background: "#007bff",
              color: "white",
              border: "none",
              padding: "10px 20px",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
            }}
          >
            Join
          </button>
        )}
      </div>
    )
  );
}
