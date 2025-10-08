export interface AgentData {
    timestamp: number;
    agent_id: string;
    system_info: {
        os_platform: string;
        os_version: string;
        hostname: string;
        cpu: {
            cpu_percent: number;
            cpu_count: number;
        };
        memory: {
            percent: number;
            total: number;
        };
    };
    processes: Array<{
        pid: number;
        name: string;
        username: string;
        cmdline: string;
    }>;
    connections: Array<any>; // Placeholder, refine as needed
    network_intelligence: {
        gateway_ip: string;
        router_assessment: {
            ports: { [key: string]: string };
        };
    };
}

export interface Agent {
    agent_id: string;
    last_seen: string;
    os_platform: string;
    hostname: string;
}

export interface Alert {
    title: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    evidence: any;
    ai_analysis?: {
        summary: string;
        mitre_id: string;
        remediation_plan: string[];
    };
}

export async function getAgents(): Promise<Agent[]> {
    const response = await fetch('http://127.0.0.1:8000/agents');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.agents;
}

export async function getAgentData(agentId: string): Promise<AgentData> {
    const response = await fetch(`http://127.0.0.1:8000/agents/${agentId}/latest`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

export async function getAlerts(): Promise<Alert[]> {
    const response = await fetch('http://127.0.0.1:8000/alerts');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.alerts;
}

export async function containAgent(agentId: string): Promise<any> {
    const response = await fetch(`http://127.0.0.1:8000/agents/${agentId}/contain`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}