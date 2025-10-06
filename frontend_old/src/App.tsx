import React, { useState } from 'react';
import { AssetList } from './components/AssetList';
import { getAgentData } from './api';

function App() {
    const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
    const [agentData, setAgentData] = useState<any>(null);

    const handleAgentSelect = async (agentId: string) => {
        setSelectedAgentId(agentId);
        const data = await getAgentData(agentId);
        setAgentData(data);
    };

    return (
        <div className="flex h-screen bg-gray-900">
            {/* Sidebar */}
            <div className="w-80 border-r border-gray-700">
                <AssetList onSelectAgent={handleAgentSelect} />
            </div>

            {/* Main Content */}
            <div className="flex-1 p-6">
                {selectedAgentId ? (
                    agentData ? (
                        <div className="text-white">
                            <h1 className="text-2xl font-bold mb-6">
                                Asset Details: {agentData.system_info.hostname}
                            </h1>
                            
                            {/* System Info */}
                            <div className="bg-gray-800 p-4 rounded-lg mb-4">
                                <h2 className="text-xl font-semibold mb-2">System Information</h2>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-gray-400">Platform</p>
                                        <p>{agentData.system_info.os_platform} {agentData.system_info.os_version}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400">CPU Usage</p>
                                        <p>{agentData.system_info.cpu.cpu_percent}%</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400">Memory Usage</p>
                                        <p>{agentData.system_info.memory.percent}%</p>
                                    </div>
                                </div>
                            </div>

                            {/* Network Info */}
                            <div className="bg-gray-800 p-4 rounded-lg mb-4">
                                <h2 className="text-xl font-semibold mb-2">Network Intelligence</h2>
                                <div>
                                    <p className="text-gray-400">Gateway IP</p>
                                    <p>{agentData.network_intelligence.gateway_ip}</p>
                                </div>
                            </div>

                            {/* Process List */}
                            <div className="bg-gray-800 p-4 rounded-lg">
                                <h2 className="text-xl font-semibold mb-2">Running Processes</h2>
                                <div className="max-h-60 overflow-y-auto">
                                    {agentData.processes.slice(0, 10).map((process: any) => (
                                        <div key={process.pid} className="mb-2">
                                            <p className="font-medium">{process.name}</p>
                                            <p className="text-sm text-gray-400">PID: {process.pid}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-white">Loading asset data...</div>
                    )
                ) : (
                    <div className="text-gray-500 text-center mt-10">
                        Select an asset from the sidebar to view details
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
