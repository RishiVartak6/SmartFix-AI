import {
  SystemHealth,
  DiagnosisSessionResponse,
  RepairCatalogItem,
  RepairExecutionResult,
  HistoryResponse,
  AppSettingsData,
  EventLogItem,
  ProcessItem,
  NetworkInfo
} from '../types';

const API_BASE = 'http://127.0.0.1:8000/api';

export const api = {
  // System Health & Diagnostics
  getHealth: async (): Promise<SystemHealth> => {
    const res = await fetch(`${API_BASE}/system/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  getSystemInfo: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/system/info`);
    return res.json();
  },

  getEvents: async (hours = 24, max = 30): Promise<EventLogItem[]> => {
    const res = await fetch(`${API_BASE}/system/events?hours=${hours}&max_events=${max}`);
    return res.json();
  },

  getServices: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/system/services`);
    return res.json();
  },

  getProcesses: async (limit = 15): Promise<{ top_by_cpu: ProcessItem[]; top_by_ram: ProcessItem[] }> => {
    const res = await fetch(`${API_BASE}/system/processes?limit=${limit}`);
    return res.json();
  },

  getNetwork: async (): Promise<NetworkInfo> => {
    const res = await fetch(`${API_BASE}/system/network`);
    return res.json();
  },

  // Diagnosis
  diagnose: async (mode: 'full_scan' | 'user_query', userQuery?: string): Promise<DiagnosisSessionResponse> => {
    const res = await fetch(`${API_BASE}/diagnosis/diagnose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, user_query: userQuery })
    });
    if (!res.ok) throw new Error('Diagnosis failed to complete');
    return res.json();
  },

  // Repairs
  getRepairsCatalog: async (): Promise<{ catalog: RepairCatalogItem[]; is_admin: boolean }> => {
    const res = await fetch(`${API_BASE}/repairs`);
    return res.json();
  },

  approveRepair: async (repairId: string, diagnosisId?: string, sessionId?: string) => {
    const res = await fetch(`${API_BASE}/repairs/${repairId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repair_id: repairId, diagnosis_id: diagnosisId, session_id: sessionId })
    });
    return res.json();
  },

  executeRepair: async (repairId: string, diagnosisId?: string, sessionId?: string): Promise<RepairExecutionResult> => {
    const res = await fetch(`${API_BASE}/repairs/${repairId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repair_id: repairId, diagnosis_id: diagnosisId, session_id: sessionId })
    });
    if (!res.ok) throw new Error('Repair execution failed');
    return res.json();
  },

  // History
  getHistory: async (limit = 30): Promise<HistoryResponse> => {
    const res = await fetch(`${API_BASE}/history?limit=${limit}`);
    return res.json();
  },

  clearHistory: async () => {
    const res = await fetch(`${API_BASE}/history/clear`, { method: 'DELETE' });
    return res.json();
  },

  // Settings & Ollama
  getSettings: async (): Promise<AppSettingsData> => {
    const res = await fetch(`${API_BASE}/settings`);
    return res.json();
  },

  updateSettings: async (payload: { ollama_host?: string; ollama_model?: string; ollama_timeout?: number }) => {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  },

  testOllama: async (host?: string) => {
    const url = host ? `${API_BASE}/settings/test-ollama?host=${encodeURIComponent(host)}` : `${API_BASE}/settings/test-ollama`;
    const res = await fetch(url, { method: 'POST' });
    return res.json();
  },

  // Demo Fault Simulator
  simulateFault: async (faultType: string) => {
    const res = await fetch(`${API_BASE}/demo/simulate-fault`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fault_type: faultType })
    });
    return res.json();
  },

  restoreAllDemoServices: async () => {
    const res = await fetch(`${API_BASE}/demo/restore-all`, { method: 'POST' });
    return res.json();
  }
};
