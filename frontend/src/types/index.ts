export interface SystemHealth {
  health_status: 'Healthy' | 'Attention Required' | 'Critical';
  attention_reasons: string[];
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_status: string;
  dns_healthy: boolean;
  failed_services_count: number;
  failed_critical_services: CriticalService[];
  total_services: number;
  recent_event_errors: number;
  uptime_hours: number;
}

export interface CriticalService {
  name: string;
  display_name: string;
  status: string;
  start_type: string;
  category: string;
  is_degraded: boolean;
}

export interface DiagnosisItem {
  id: string;
  problem: string;
  probable_root_cause: string;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low';
  severity: 'low' | 'medium' | 'high' | 'critical';
  evidence: string[];
  recommended_repair_id: string | null;
  explanation: string;
}

export interface DiagnosisSessionResponse {
  session_id: string;
  diagnostics_summary: {
    health_status: string;
    attention_reasons: string[];
    cpu_percent: number;
    memory_percent: number;
    network_status: string;
  };
  diagnoses: DiagnosisItem[];
}

export interface RepairCatalogItem {
  id: string;
  name: string;
  category: string;
  risk: 'low' | 'medium' | 'high';
  requires_admin: boolean;
  description: string;
  verification: string;
}

export interface RepairExecutionResult {
  record_id: string;
  repair_id: string;
  repair_name: string;
  success: boolean;
  execution_output: string;
  error_message: string | null;
  verified: boolean;
  verification_success: boolean;
  verification_message: string;
  verification_details: Record<string, any>;
  duration_ms: number;
}

export interface HistoryResponse {
  repairs: {
    id: string;
    timestamp: string;
    repair_id: string;
    repair_name: string;
    status: string;
    requires_admin: boolean;
    verification_success: boolean;
    verification_message: string;
    execution_output: string;
    error_message: string | null;
    duration_ms: number;
  }[];
  sessions: {
    id: string;
    timestamp: string;
    mode: string;
    problem_description: string;
    status: string;
  }[];
  total_repairs: number;
  total_sessions: number;
}

export interface EventLogItem {
  event_id: number;
  provider: string;
  log_name: string;
  level: string;
  timestamp: string;
  message: string;
}

export interface ProcessItem {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  memory_mb: number;
  is_protected: boolean;
}

export interface NetworkInfo {
  interfaces: {
    interface: string;
    is_up: boolean;
    speed_mbps: number;
    ipv4: string[];
    is_loopback: boolean;
  }[];
  has_active_adapter: boolean;
  dns_healthy: boolean;
  dns_google_ok: boolean;
  dns_cloudflare_ok: boolean;
  status: string;
  io_summary: {
    bytes_sent_mb: number;
    bytes_recv_mb: number;
    errin: number;
    errout: number;
  };
}

export interface AppSettingsData {
  app_name: string;
  app_version: string;
  ollama_host: string;
  ollama_model: string;
  ollama_timeout: number;
  ollama_status: {
    available: boolean;
    host: string;
    models: string[];
    configured_model: string;
    model_installed: boolean;
  };
  is_admin: boolean;
}
