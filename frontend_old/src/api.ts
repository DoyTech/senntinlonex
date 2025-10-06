import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000'
});

export const getAgents = async () => {
    try {
        const response = await api.get('/agents');
        return response.data.agents;
    } catch (error) {
        console.error('Error fetching agents:', error);
        return [];
    }
};

export const getAgentData = async (agentId: string) => {
    try {
        const response = await api.get(`/agents/${agentId}/latest`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching agent ${agentId} data:`, error);
        return null;
    }
};
