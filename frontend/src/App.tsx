import { useState, useEffect } from 'react';
import { getAgents, getAgentData, Agent, AgentData } from './api';
import AssetList from './components/AssetList';
import AgentDetails from './components/AgentDetails';

function App() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentData | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const agentList = await getAgents();
        setAgents(agentList);
      } catch (error) {
        console.error('Error fetching agents:', error);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleAgentSelect = async (agentId: string) => {
    try {
      const agentData = await getAgentData(agentId);
      if (agentData) {
        setSelectedAgent(agentData);
      }
    } catch (error) {
      console.error('Error fetching agent details:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white shadow-md">
        <AssetList agents={agents} onSelectAgent={handleAgentSelect} />
      </aside>
      <main className="flex-1 p-6">
        {selectedAgent ? (
          <AgentDetails agentData={selectedAgent} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select an agent to view details
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
