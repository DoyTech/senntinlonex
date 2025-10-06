import React from 'react';
import { Agent } from '../api';

interface AssetListProps {
  agents: Agent[];
  onSelectAgent: (agentId: string) => void;
}

const AssetList: React.FC<AssetListProps> = ({ agents, onSelectAgent }) => {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Connected Agents</h2>
      <div className="space-y-2">
        {agents.map((agent) => (
          <button
            key={agent.agent_id}
            onClick={() => onSelectAgent(agent.agent_id)}
            className="w-full text-left p-3 rounded bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div className="font-medium">{agent.hostname}</div>
            <div className="text-sm text-gray-600">
              {agent.os_platform}
            </div>
            <div className="text-xs text-gray-500">
              Last seen: {new Date(agent.last_seen).toLocaleString()}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default AssetList;
