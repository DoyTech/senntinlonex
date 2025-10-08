import React, { useState, useEffect } from 'react';
import { getAlerts, containAgent } from '../api';
import { Alert } from '../types';

const AlertsDashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      const fetchedAlerts = await getAlerts();
      setAlerts(fetchedAlerts);
    };

    fetchAlerts();
    const intervalId = setInterval(fetchAlerts, 3000);
    return () => clearInterval(intervalId);
  }, []);

  const handleContainAgent = async (agentId: string) => {
    await containAgent(agentId);
    alert(`Containment command issued for agent: ${agentId}`);
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-900 border-red-500';
      case 'high': return 'bg-orange-900 border-orange-500';
      default: return 'bg-gray-700 border-gray-500';
    }
  };

  return (
    <div className="grid grid-cols-3 h-full">
      <div className="col-span-1 p-4 border-r border-gray-700 overflow-y-auto">
        <h2 className="text-xl font-bold text-white mb-4">Live Alerts</h2>
        {alerts.length > 0 ? (
          alerts.map((alert) => (
            <div
              key={alert.id}
              onClick={() => setSelectedAlert(alert)}
              className={`p-3 rounded mb-2 cursor-pointer border-l-4 ${getSeverityClass(alert.severity)} ${selectedAlert?.id === alert.id ? 'bg-gray-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              <p className="font-bold text-white">{alert.title}</p>
              <p className="text-sm text-gray-400">Agent: {alert.agent_id}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No alerts detected.</p>
        )}
      </div>
      <div className="col-span-2 p-4 overflow-y-auto">
        {selectedAlert ? (
          <div>
            <h2 className="text-2xl font-bold text-blue-400 mb-2">{selectedAlert.title}</h2>
            <p className="text-lg text-gray-300 mb-4">Agent: <span className="font-mono">{selectedAlert.agent_id}</span></p>
            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-bold text-white mb-2">Virtual Analyst Report</h3>
              <p className="text-gray-300 mb-2"><span className="font-bold">Summary:</span> {selectedAlert.ai_analysis?.summary}</p>
              <p className="text-gray-300 mb-2"><span className="font-bold">MITRE ATT&CK:</span> <span className="font-mono text-orange-400">{selectedAlert.ai_analysis?.mitre_technique}</span></p>
              <p className="text-gray-300"><span className="font-bold">Remediation:</span> {selectedAlert.ai_analysis?.remediation}</p>
            </div>
            <button
              onClick={() => handleContainAgent(selectedAlert.agent_id)}
              className="mt-6 w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
            >
              Contain Host: {selectedAlert.agent_id}
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