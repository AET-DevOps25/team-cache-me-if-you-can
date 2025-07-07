import { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from "react"; // Added useRef
import { GroupData } from "../../../models/GroupData";
import { useAuth } from "../../../auth/AuthProvider";

interface GroupContextType {
  currentGroup: GroupData | null;
  setCurrentGroup: (group: GroupData | null) => void;
  groups: GroupData[] | null;
  refreshGroups: () => Promise<void>;
  updateGroupInList: (updatedGroup: GroupData) => void;
}

const GroupContext = createContext<GroupContextType | undefined>(undefined);

export function GroupProvider({ children }: { children: ReactNode }) {
  const [currentGroup, _setCurrentGroup] = useState<GroupData | null>(null); // Renamed to _setCurrentGroup
  const setCurrentGroup = useCallback((group: GroupData | null) => { // Memoize setCurrentGroup as well
    _setCurrentGroup(group);
  }, []);

  const [allGroups, setAllGroups] = useState<GroupData[] | null>(null);
  const auth = useAuth();

  // Use a ref to hold the *latest* currentGroup value without making it a useCallback dependency
  const currentGroupRef = useRef(currentGroup);
  useEffect(() => {
    currentGroupRef.current = currentGroup;
  }, [currentGroup]);


  const refreshGroups = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/groups", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
        },
      });
      if (!response.ok) throw new Error("Failed to fetch groups");

      const data: GroupData[] = await response.json();
      setAllGroups(data);

      // Update current group if it exists
      if (currentGroupRef.current) {
        const updatedGroup = data.find(g => g.id === currentGroupRef.current?.id);
        if (updatedGroup) {
          setCurrentGroup(updatedGroup);
        }
      }
    } catch (error) {
      console.error("Error refreshing groups:", error);
      setAllGroups([]);
    }
  }, [auth.token, setCurrentGroup]);

  useEffect(() => {
    refreshGroups();
  }, [auth.user, refreshGroups]);

  const updateGroupInList = useCallback((updatedGroup: GroupData) => {
    setAllGroups(prevGroups => {
      if (!prevGroups) return null;
      return prevGroups.map(group =>
          group.id === updatedGroup.id ? updatedGroup : group
      );
    });
  }, []);

  return (
      <GroupContext.Provider
          value={{
            currentGroup, // Use currentGroup state here
            setCurrentGroup,
            groups: allGroups,
            refreshGroups,
            updateGroupInList
          }}
      >
        {children}
      </GroupContext.Provider>
  );
}

export function useGroup() {
  const context = useContext(GroupContext);
  if (!context) {
    throw new Error("useGroup must be used within a GroupProvider");
  }
  return context;
}