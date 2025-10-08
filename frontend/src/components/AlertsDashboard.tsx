import React, { useState, useEffect } from 'react';
import { getAlerts, containAgent, Alert as ApiAlert } from '../api';

// Define the structure of an Alert object for the UI, extending from the API's Alert
interface Alert extends ApiAlert {
  id: string; // Add a unique ID for React keys
}

const AlertsDashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      const fetchedApiAlerts = await getAlerts();
      // Add a unique ID to each alert for React's key prop
      const alertsWithIds: Alert[] = fetchedApiAlerts.map((alert, index) => ({
        ...alert,
        id: alert.evidence.agent_id + "-" + alert.title + "-" + index, // Simple unique ID for demo
      }));
      setAlerts(alertsWithIds);
    };

    fetchAlerts();
    const intervalId = setInterval(fetchAlerts, 3000); // Fetch every 3 seconds
    return () => clearInterval(intervalId);
  }, []);

  const handleContainAgent = async (agentId: string) => {
    await containAgent(agentId);
    alert(`Containment command issued for agent: ${agentId}`);
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-800 border-red-500';
      case 'high': return 'bg-orange-800 border-orange-500';
      case 'medium': return 'bg-yellow-800 border-yellow-500';
      case 'low': return 'bg-green-800 border-green-500';
      default: return 'bg-gray-700 border-gray-500';
    }
  };

  return (
    <div className="grid grid-cols-3 h-full">
      {/* Alerts List */}
      <div className="col-span-1 p-4 border-r border-gray-700 overflow-y-auto">
        <h2 className="text-xl font-bold text-white mb-4">Live Alerts</h2>
        {alerts.map((alert) => (
          <div
            key={alert.id}
            onClick={() => setSelectedAlert(alert)}
            className={`p-3 rounded mb-2 cursor-pointer border-l-4 ${getSeverityClass(alert.severity)} ${selectedAlert?.id === alert.id ? 'bg-gray-600' : 'bg-gray-800 hover:bg-gray-700'}`}
          >
            <p className="font-bold text-white">{alert.title}</p>
            <p className="text-sm text-gray-400">Agent: {alert.evidence.agent_id}</p>
          </div>
        ))}
      </div>

      {/* Alert Details */}
      <div className="col-span-2 p-4 overflow-y-auto">
        {selectedAlert ? (
          <div>
            <h2 className="text-2xl font-bold text-blue-400 mb-2">{selectedAlert.title}</h2>
            <p className="text-lg text-gray-300 mb-4">Agent: <span className="font-mono">{selectedAlert.evidence.agent_id}</span></p>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-white mb-2">Virtual Analyst Report</h3>
              <p className="text-gray-300 mb-2"><span className="font-bold text-white">Summary:</span> {selectedAlert.ai_analysis?.summary}</p>
              <p className="text-gray-300 mb-2"><span className="font-bold text-white">MITRE ATT&CK:</span> <span className="font-mono text-orange-400">{selectedAlert.ai_analysis?.mitre_id}</span></p>
              <p className="text-gray-300"><span className="font-bold text-white">Remediation:</span> {selectedAlert.ai_analysis?.remediation_plan?.join(' ')}</p>
            </div>

            <button
              onClick={() => handleContainAgent(selectedAlert.evidence.agent_id)}
              className="mt-6 w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg"
            >
              Contain Host: {selectedAlert.evidence.agent_id}
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Select an alert to view details.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsDashboard;