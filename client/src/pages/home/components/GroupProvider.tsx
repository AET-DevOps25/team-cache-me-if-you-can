/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, ReactNode } from "react";
import { GroupData } from "../../../models/GroupData";

interface GroupProviderProps {
  children: ReactNode;
}

interface GroupContextType {
  currentGroup: GroupData | null;
  setCurrentGroup: (group: GroupData | null) => void;
}

const GroupContext = createContext<GroupContextType | undefined>(undefined);

const GroupProvider: React.FC<GroupProviderProps> = ({ children }) => {
  const [currentGroup, setCurrentGroup] = useState<GroupData | null>(null);

  return (
    <GroupContext.Provider value={{ currentGroup, setCurrentGroup }}>
      {children}
    </GroupContext.Provider>
  );
};

export default GroupProvider;

export const useGroup = () => {
  const context = useContext(GroupContext);
  if (!context) {
    throw new Error("useGroup must be used within a GroupProvider");
  }
  return context;
};
