export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: 'SOC_ADMIN' | 'SOC_ANALYST' | 'INCIDENT_RESPONDER' | 'SECURITY_VIEWER' | 'Admin' | 'Analyst' | 'Auditor' | 'Responder' | 'Viewer' | string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}


export interface RiskFactor {
  factor: string;
  contribution: number;
}

export interface LogEvent {
  id: number;
  timestamp: string;
  log_source: string;
  event_type: string;
  source_ip?: string;
  destination_ip?: string;
  source_port?: number;
  destination_port?: number;
  user_name?: string;
  hostname?: string;
  action?: string;
  severity: 'INFORMATIONAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  raw_message: string;
  anomaly_score: number;
  is_anomaly: 'NORMAL' | 'ANOMALOUS';
  model_version?: string;
  correlation_id?: string;
}

export interface SecurityAlert {
  id: number;
  title: string;
  description: string;
  rule_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category: string;
  mitre_tactic?: string;
  mitre_technique?: string;
  source_ip?: string;
  destination_ip?: string;
  affected_asset?: string;
  risk_score: number;
  detection_source?: 'RULE_BASED' | 'ML_ANOMALY' | 'HYBRID';
  risk_factors?: RiskFactor[];
  anomaly_score?: number;
  status: 'NEW' | 'INVESTIGATING' | 'IN_PROGRESS' | 'RESOLVED' | 'FALSE_POSITIVE';
  created_at: string;
  correlation_id?: string;
  source_event_ids?: number[];
}

export interface Incident {
  id: number;
  incident_number: string;
  title: string;
  summary: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'CONTAINMENT' | 'REMEDIATION' | 'CLOSED';
  assignee?: string;
  affected_systems?: string[];
  mitre_tactics?: string[];
  ai_recommendation?: string;
  created_at: string;
  updated_at: string;
  correlation_id?: string;
}

export interface CorrelationGroup {
  id: number;
  correlation_id: string;
  title: string;
  stage_summary?: string;
  source_ip?: string;
  target_asset?: string;
  event_ids: number[];
  alert_ids: number[];
  event_count: number;
  risk_score: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: string;
  first_seen: string;
  last_seen: string;
  mitre_tactics?: string[];
}

export interface ThreatIntel {
  id: number;
  ioc_value: string;
  ioc_type: 'IP' | 'MD5' | 'SHA256' | 'DOMAIN' | 'URL';
  threat_type?: string;
  threat_score: number;
  source_feed?: string;
  description?: string;
  last_updated: string;
}

export interface AuditLogItem {
  id: number;
  timestamp: string;
  actor_username: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  status: string;
  ip_address?: string;
  details?: string;
}

export interface AnalyticsSummary {
  metrics: {
    total_logs: number;
    anomalous_logs: number;
    total_alerts: number;
    critical_alerts: number;
    high_alerts: number;
    open_incidents: number;
    mttd_seconds?: number;
    mttr_seconds?: number;
    precision?: number;
    recall?: number;
    alert_reduction_percent?: number;
    threat_level: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'CRITICAL';
  };
  severity_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  detection_source_distribution?: Record<string, number>;
}

export interface CopilotResponse {
  answer: string;
  action_items: string[];
  mitre_references: string[];
  confidence_score: number;
  analysis_details: Record<string, any>;
  what_happened?: string;
  why_generated?: string;
  evidence_items?: string[];
  risk_explanation?: string;
  correlated_events_summary?: string;
  threat_intel_context?: string;
  investigation_steps?: string[];
  recommended_remediation?: string[];
  uncertainty_statement?: string;
}
