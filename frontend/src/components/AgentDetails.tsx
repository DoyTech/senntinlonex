import React from 'react';
import { AgentData } from '../api';

interface AgentDetailsProps {
    agentData: AgentData;
}

export const AgentDetails: React.FC<AgentDetailsProps> = ({ agentData }) => {
    const formatBytes = (bytes: number): string => {
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
    };

    return (
        <div className="p-6 text-white">
            <h1 className="text-2xl font-bold mb-6">
                {agentData.system_info.hostname}
            </h1>

            {/* System Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-800 p-4 rounded-lg">
                    <h2 className="text-xl font-semibold mb-4">System Information</h2>
                    <div className="space-y-2">
                        <div>
                            <span className="text-gray-400">OS: </span>
                            <span>{agentData.system_info.os_platform} {agentData.system_info.os_version}</span>
                        </div>
                        <div>
                            <span className="text-gray-400">CPU Usage: </span>
                            <span>{agentData.system_info.cpu.cpu_percent}%</span>
                        </div>
                        <div>
                            <span className="text-gray-400">CPU Cores: </span>
                            <span>{agentData.system_info.cpu.cpu_count}</span>
                        </div>
                        <div>
                            <span className="text-gray-400">Memory Usage: </span>
                            <span>{agentData.system_info.memory.percent}%</span>
                        </div>
                        <div>
                            <span className="text-gray-400">Memory Total: </span>
                            <span>{formatBytes(agentData.system_info.memory.total)}</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 p-4 rounded-lg">
                    <h2 className="text-xl font-semibold mb-4">Network Intelligence</h2>
                    <div className="space-y-2">
                        <div>
                            <span className="text-gray-400">Gateway IP: </span>
                            <span>{agentData.network_intelligence.gateway_ip}</span>
                        </div>
                        <div>
                            <span className="text-gray-400">Open Ports: </span>
                            <div className="ml-2">
                                {Object.entries(agentData.network_intelligence.router_assessment.ports)
                                    .filter(([_, status]) => status === 'open')
                                    .map(([port]) => (
                                        <span key={port} className="inline-block bg-blue-600 px-2 py-1 rounded text-sm mr-2">
                                            {port}
                                        </span>
                                    ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Processes */}
            <div className="bg-gray-800 p-4 rounded-lg mb-6">
                <h2 className="text-xl font-semibold mb-4">Running Processes</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead>
                            <tr className="text-left text-gray-400">
                                <th className="p-2">PID</th>
                                <th className="p-2">Name</th>
                                <th className="p-2">User</th>
                                <th className="p-2">Command</th>
                            </tr>
                        </thead>
                        <tbody>
                            {agentData.processes.slice(0, 10).map((process) => (
                                <tr key={process.pid} className="border-t border-gray-700">
                                    <td className="p-2">{process.pid}</td>
                                    <td className="p-2">{process.name}</td>
                                    <td className="p-2">{process.username}</td>
                                    <td className="p-2 truncate max-w-md">{process.cmdline}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Network Connections */}
            <div className="bg-gray-800 p-4 rounded-lg">
                <h2 className="text-xl font-semibold mb-4">Network Connections</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead>
                            <tr className="text-left text-gray-400">
                                <th className="p-2">Local Address</th>
                                <th className="p-2">Remote Address</th>
                                <th className="p-2">Status</th>
                                <th className="p-2">PID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {agentData.connections.slice(0, 10).map((conn, idx) => (
                                <tr key={idx} className="border-t border-gray-700">
                                    <td className="p-2">{conn.local_address || '-'}</td>
                                    <td className="p-2">{conn.remote_address || '-'}</td>
                                    <td className="p-2">{conn.status}</td>
                                    <td className="p-2">{conn.pid}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
