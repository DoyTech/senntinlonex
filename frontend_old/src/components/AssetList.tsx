import React, { useState, useEffect } from 'react';
import { getAgents } from '../api';

interface Agent {
    agent_id: string;
    hostname: string;
    os_platform: string;
    last_seen: string;
}

interface AssetListProps {
    onSelectAgent: (agentId: string) => void;
}

export const AssetList: React.FC<AssetListProps> = ({ onSelectAgent }) => {
    const [agents, setAgents] = useState<Agent[]>([]);

    useEffect(() => {
        const fetchAgents = async () => {
            const agentData = await getAgents();
            setAgents(agentData);
        };

        // Initial fetch
        fetchAgents();

        // Set up polling every 5 seconds
        const interval = setInterval(fetchAgents, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-gray-800 text-white p-4 h-full overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Assets</h2>
            <div className="space-y-2">
                {agents.map((agent) => (
                    <div
                        key={agent.agent_id}
                        onClick={() => onSelectAgent(agent.agent_id)}
                        className="p-3 bg-gray-700 rounded cursor-pointer hover:bg-gray-600 transition-colors"
                    >
                        <div className="font-medium">{agent.hostname}</div>
                        <div className="text-sm text-gray-400">{agent.os_platform}</div>
                        <div className="text-xs text-gray-500">
                            Last seen: {new Date(agent.last_seen).toLocaleString()}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
