import axios from 'axios';
import { 
  User, 
  LogEvent, 
  SecurityAlert, 
  Incident, 
  ThreatIntel, 
  AnalyticsSummary,
  CopilotResponse,
  AuditLogItem,
  CorrelationGroup
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests to inject Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('soc_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await axios.post(`${API_BASE}/auth/token`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  getUsers: async (params?: { search?: string; role?: string; is_active?: boolean }): Promise<User[]> => {
    const response = await api.get('/auth/users', { params });
    return response.data;
  },
  createUser: async (userData: { email: string; username: string; full_name?: string; role: string; password: string }): Promise<User> => {
    const response = await api.post('/auth/users', userData);
    return response.data;
  },
  updateUser: async (id: number, data: { full_name?: string; role?: string; is_active?: boolean }): Promise<User> => {
    const response = await api.put(`/auth/users/${id}`, data);
    return response.data;
  },
  toggleUserStatus: async (id: number, isActive: boolean): Promise<User> => {
    const response = await api.put(`/auth/users/${id}/status`, { is_active: isActive });
    return response.data;
  },
  resetPassword: async (id: number, newPassword: string) => {
    const response = await api.put(`/auth/users/${id}/reset-password`, { new_password: newPassword });
    return response.data;
  },
};


export const logsApi = {
  getLogs: async (params?: { source?: string; severity?: string; anomaly_only?: boolean; limit?: number }): Promise<LogEvent[]> => {
    const response = await api.get('/logs/', { params });
    return response.data;
  },
  ingestLog: async (logData: Partial<LogEvent>): Promise<LogEvent> => {
    const response = await api.post('/logs/', logData);
    return response.data;
  },
  simulateScenario: async (scenarioType: string): Promise<LogEvent> => {
    const response = await api.post(`/logs/simulate-scenario?scenario_type=${scenarioType}`);
    return response.data;
  },
};

export const alertsApi = {
  getAlerts: async (params?: { severity?: string; status?: string; limit?: number }): Promise<SecurityAlert[]> => {
    const response = await api.get('/alerts/', { params });
    return response.data;
  },
  getAlert: async (id: number): Promise<SecurityAlert> => {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },
  updateStatus: async (id: number, status: string): Promise<SecurityAlert> => {
    const response = await api.patch(`/alerts/${id}/status`, { status });
    return response.data;
  },
};

export const correlationsApi = {
  getCorrelations: async (): Promise<CorrelationGroup[]> => {
    const response = await api.get('/correlations/');
    return response.data;
  },
  getCorrelationDetail: async (id: string) => {
    const response = await api.get(`/correlations/${id}`);
    return response.data;
  },
};

export const evaluationApi = {
  runEvaluation: async (nSamples: number = 1000) => {
    const response = await api.get(`/evaluation/run?n_samples=${nSamples}`);
    return response.data;
  },
  getLatestEvaluation: async () => {
    const response = await api.get('/evaluation/latest');
    return response.data;
  },
};

export const feedbackApi = {
  submitFeedback: async (feedback: { alert_id?: number; incident_id?: number; feedback_type: string; comments?: string }) => {
    const response = await api.post('/feedback/', feedback);
    return response.data;
  },
};

export const mlApi = {
  getStatus: async () => {
    const response = await api.get('/ml/status');
    return response.data;
  },
  updateThreshold: async (threshold: number) => {
    const response = await api.post('/ml/threshold', { threshold });
    return response.data;
  },
};

export const incidentsApi = {
  getIncidents: async (params?: { status?: string; severity?: string }): Promise<Incident[]> => {
    const response = await api.get('/incidents/', { params });
    return response.data;
  },
  createIncident: async (data: Partial<Incident>): Promise<Incident> => {
    const response = await api.post('/incidents/', data);
    return response.data;
  },
  updateIncident: async (id: number, data: Partial<Incident>): Promise<Incident> => {
    const response = await api.put(`/incidents/${id}`, data);
    return response.data;
  },
  executeContainmentAction: async (id: number, actionType: string) => {
    const response = await api.post(`/incidents/${id}/containment-action?action_type=${actionType}`);
    return response.data;
  },
};

export const threatIntelApi = {
  getThreatIntel: async (params?: { ioc_type?: string }): Promise<ThreatIntel[]> => {
    const response = await api.get('/intelligence/', { params });
    return response.data;
  },
  addIoc: async (ioc: Partial<ThreatIntel>): Promise<ThreatIntel> => {
    const response = await api.post('/intelligence/', ioc);
    return response.data;
  },
  lookupIoc: async (iocValue: string): Promise<ThreatIntel> => {
    const response = await api.get(`/intelligence/lookup/${encodeURIComponent(iocValue)}`);
    return response.data;
  },
  lookupCve: async (cveId: string) => {
    const response = await api.get(`/intelligence/cve/${encodeURIComponent(cveId)}`);
    return response.data;
  },
};

export const copilotApi = {
  queryCopilot: async (query: string, alertId?: number, incidentId?: number): Promise<CopilotResponse> => {
    const response = await api.post('/copilot/query', {
      query,
      context_alert_id: alertId,
      context_incident_id: incidentId,
    });
    return response.data;
  },
};

export const analyticsApi = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    const response = await api.get('/analytics/summary');
    return response.data;
  },
};

export const auditApi = {
  getAuditLogs: async (params?: { actor?: string; action?: string }): Promise<AuditLogItem[]> => {
    const response = await api.get('/audit/', { params });
    return response.data;
  },
};

export default api;
