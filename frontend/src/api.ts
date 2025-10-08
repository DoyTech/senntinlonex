import axios from 'axios';
import { Alert } from './types'; // We will create this types file

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
});

export const getAgentList = async (): Promise<string[]> => {
  try {
    const response = await apiClient.get('/agents');
    return response.data.agents || [];
  } catch (error) {
    console.error("Failed to fetch agent list:", error);
    return [];
  }
};

export const getAlerts = async (): Promise<Alert[]> => {
  try {
    const response = await apiClient.get('/alerts');
    return response.data.alerts || [];
  } catch (error) {
    console.error("Failed to fetch alerts:", error);
    return [];
  }
};

export const containAgent = async (agentId: string) => {
  try {
    const response = await apiClient.post(`/agents/${agentId}/contain`);
    return response.data;
  } catch (error) {
    console.error(`Failed to issue containment for ${agentId}:`, error);
    return null;
  }
};