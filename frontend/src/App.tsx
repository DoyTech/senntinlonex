import { useState, useEffect } from 'react';
import { getAgents, Agent } from './api';
import AssetList from './components/AssetList';
import AlertsDashboard from './components/AlertsDashboard';

function App() {
  const [agents, setAgents] = useState<Agent[]>([]);

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

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <aside className="w-64 bg-gray-800 shadow-md">
        <AssetList agents={agents} onSelectAgent={() => {}} />
      </aside>
      <main className="flex-1">
        <AlertsDashboard />
      </main>
    </div>
  );
}

export default App;
