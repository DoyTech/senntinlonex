import React, { useState, useEffect } from 'react';
import { getAgentList } from '../api';

interface Agent {
  agent_id: string;
  // We'll assume a basic structure for now, as the backend only returns agent_ids
  // In a real app, this would be more detailed.
}

const AssetList: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    const fetchAgents = async () => {
      const fetchedAgentIds = await getAgentList();
      // Convert agent IDs to Agent objects for consistent rendering
      setAgents(fetchedAgentIds.map(id => ({ agent_id: id })));
    };

    fetchAgents();
    const intervalId = setInterval(fetchAgents, 5000); // Refresh every 5 seconds
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Connected Agents</h2>
      <div className="space-y-2">
        {agents.length > 0 ? (
          agents.map((agent) => (
            <button
              key={agent.agent_id}
              // onClick={() => onSelectAgent(agent.agent_id)} // Re-enable if needed later
              className="w-full text-left p-3 rounded bg-gray-800 hover:bg-gray-700 transition-colors text-white"
            >
              <div className="font-medium">{agent.agent_id}</div>
              {/* <div className="text-sm text-gray-400">{agent.os_platform}</div> */}
              {/* <div className="text-xs text-gray-500">Last seen: {new Date(agent.last_seen).toLocaleString()}</div> */}
            </button>
          ))
        ) : (
          <p className="text-gray-500">No agents connected.</p>
        )}
      </div>
    </div>
  );
};

export default AssetList;
