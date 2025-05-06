import { useEffect, useState } from 'react';
import './group.css';

export default function Group() {
    const [groups, setGroups] = useState<Array<{id: number, name: string}> | null>(null);
    
    function getGroups(){
        setGroups([
            { id: 1, name: 'Biology 101' },
            { id: 2, name: 'Computer Science' },
            { id: 3, name: 'Psychology' },
          ]);
        //TODO: get groups from api
    }
    
    function onGroupSelect(name: string) {
        //TODO: go to the group page
    }

    useEffect(() => {
        getGroups();
    }, []);
    
    return (
    <div className="groups-container">
      <h2 className="groups-title">My Groups</h2>
      
      {/* Group Tiles Container */}
      <div className="groups-tiles-container">
        {groups ? (
            groups.map(group => (
                <div 
                    key={group.id}
                    className="group-tile"
                    onClick={() => onGroupSelect(group.name)}
                />
            ))
        ) : (
            <p>Join a Group!</p>
        )}
      </div>
      
      {/* Action Buttons */}
      <div className="groups-actions">
        <button className="groups-button groups-button-margin">create</button>
        <button className="groups-button">find</button>
      </div>
    </div>
  );
}