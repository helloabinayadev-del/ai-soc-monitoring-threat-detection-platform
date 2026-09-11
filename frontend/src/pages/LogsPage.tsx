import React, { useState } from 'react';
import { useSOC } from '../context/SOCContext';
import { LogTable } from '../components/LogTable';
import { Terminal, Filter, Plus, RefreshCw, Zap } from 'lucide-react';
import { logsApi } from '../services/api';

export const LogsPage: React.FC = () => {
  const { logs, refreshData } = useSOC();
  const [anomalyOnly, setAnomalyOnly] = useState(false);
  const [selectedSource, setSelectedSource] = useState<string>('ALL');
  const [isIngestOpen, setIsIngestOpen] = useState(false);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [activeScenario, setActiveScenario] = useState('brute_force');

  // Refresh State
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string | null>(null);

  // Manual Ingestion Form State
  const [rawMsg, setRawMsg] = useState('');
  const [source, setSource] = useState('WindowsEvent');
  const [eventType, setEventType] = useState('Authentication');
  const [loading, setLoading] = useState(false);

  const filteredLogs = logs.filter((log) => {
    if (anomalyOnly && log.is_anomaly !== 'ANOMALOUS') return false;
    if (selectedSource !== 'ALL' && log.log_source !== selectedSource) return false;
    return true;
  });

  const handleRefreshLogs = async () => {
    if (isRefreshing) return;
    setIsRefreshing(true);
    setRefreshError(null);
    try {
      await refreshData();
      setLastRefreshedAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      console.error('[!] Log refresh failed:', err);
      setRefreshError('Failed to refresh security event logs from server.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await logsApi.ingestLog({
        log_source: source,
        event_type: eventType,
        raw_message: rawMsg,
        severity: 'HIGH',
        source_ip: '192.168.1.55',
        destination_ip: '10.0.0.1',
        hostname: 'WKSTN-TEST-01',
      });
      setRawMsg('');
      setIsIngestOpen(false);
      await handleRefreshLogs();
    } catch (e) {
      console.error('[!] Log ingestion failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScenario = async () => {
    setScenarioLoading(true);
    try {
      await logsApi.simulateScenario(activeScenario);
      await handleRefreshLogs();
    } catch (e) {
      console.error('[!] Scenario simulation failed:', e);
    } finally {
      setScenarioLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Terminal className="h-5 w-5 text-cyan-400" />
            Security Event Log Explorer (ECS Normalized)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Real-time multi-source log stream, machine learning anomaly scoring, and raw payload audit.
            {lastRefreshedAt && <span className="text-cyan-400 ml-2">• Refreshed at {lastRefreshedAt}</span>}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Lab Event Generator Scenario Control */}
          <div className="flex items-center space-x-1.5 bg-soc-card border border-cyan-800/80 rounded-lg p-1">
            <label htmlFor="logs-scenario-select" className="sr-only">Lab Scenario</label>
            <select
              id="logs-scenario-select"
              name="activeScenario"
              aria-label="Lab Event Generator Scenario Control"
              value={activeScenario}
              onChange={(e) => setActiveScenario(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-2.5 py-1 text-xs font-mono text-cyan-400 focus:outline-none focus:border-cyan-500"
            >
              <option value="brute_force">Lab Event: Brute Force Login</option>
              <option value="privilege_escalation">Lab Event: Sudo Privilege Escalation</option>
              <option value="powershell_stager">Lab Event: PowerShell Stager</option>
              <option value="c2_beacon">Lab Event: Outbound C2 Beacon</option>
              <option value="sqli_attack">Lab Event: SQL Injection Attack</option>
            </select>
            <button
              onClick={handleRunScenario}
              disabled={scenarioLoading}
              className="px-3 py-1 rounded bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-bold flex items-center space-x-1 transition shadow disabled:opacity-50 cursor-pointer"
              title="Generate Synthetic Security Event"
            >
              <Zap className="h-3.5 w-3.5 text-cyan-200" />
              <span>{scenarioLoading ? 'Ingesting...' : 'Run Scenario'}</span>
            </button>
          </div>

          <button
            onClick={() => setIsIngestOpen(!isIngestOpen)}
            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs flex items-center space-x-2 border border-soc-border transition cursor-pointer"
          >
            <Plus className="h-4 w-4" />
            <span>Custom Log</span>
          </button>
          
          <button
            onClick={handleRefreshLogs}
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-soc-card border border-soc-border hover:border-cyan-500 text-slate-300 transition disabled:opacity-50 flex items-center space-x-1 cursor-pointer"
            title="Refresh Security Event Logs"
            aria-label="Refresh Security Event Logs"
          >
            <RefreshCw className={`h-4 w-4 text-cyan-400 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Refresh Error Alert */}
      {refreshError && (
        <div className="p-3 rounded-lg border border-red-800 bg-red-950/80 text-red-300 text-xs font-mono flex items-center justify-between">
          <span>✕ {refreshError}</span>
          <button onClick={() => setRefreshError(null)} className="text-red-400 hover:text-white font-bold">✕</button>
        </div>
      )}

      {/* Manual Ingest Modal/Panel */}
      {isIngestOpen && (
        <form onSubmit={handleIngest} className="p-4 rounded-xl border border-cyan-800 bg-soc-card space-y-3 font-mono text-xs">
          <div className="font-semibold text-cyan-400">INGEST CUSTOM LOG SIMULATION</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="ingest-log-source" className="block text-slate-400 mb-1">LOG SOURCE</label>
              <select
                id="ingest-log-source"
                name="source"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200"
              >
                <option value="WindowsEvent">WindowsEvent</option>
                <option value="LinuxSyslog">LinuxSyslog</option>
                <option value="Firewall">Firewall</option>
                <option value="EndpointEDR">EndpointEDR</option>
                <option value="AWSCloudTrail">AWSCloudTrail</option>
              </select>
            </div>
            <div>
              <label htmlFor="ingest-event-type" className="block text-slate-400 mb-1">EVENT TYPE</label>
              <select
                id="ingest-event-type"
                name="eventType"
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200"
              >
                <option value="Authentication">Authentication</option>
                <option value="ProcessCreation">ProcessCreation</option>
                <option value="PrivilegeEscalation">PrivilegeEscalation</option>
                <option value="NetworkConnection">NetworkConnection</option>
              </select>
            </div>
          </div>
          <div>
            <label htmlFor="ingest-raw-msg" className="block text-slate-400 mb-1">RAW LOG MESSAGE</label>
            <textarea
              id="ingest-raw-msg"
              name="rawMsg"
              required
              rows={2}
              autoComplete="off"
              value={rawMsg}
              onChange={(e) => setRawMsg(e.target.value)}
              placeholder="e.g. powershell.exe -EncodedCommand SQBFA... or sudo failed login attempt..."
              className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200"
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={() => setIsIngestOpen(false)} className="px-3 py-1.5 rounded bg-slate-800 text-slate-300">Cancel</button>
            <button type="submit" disabled={loading} className="px-4 py-1.5 rounded bg-cyan-600 text-white font-bold">{loading ? 'Ingesting...' : 'Submit Log'}</button>
          </div>
        </form>
      )}

      {/* Filter Controls Bar */}
      <div className="p-4 rounded-xl border border-soc-border bg-soc-card/90 glass-panel flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <label htmlFor="logs-source-filter" className="text-slate-400">SOURCE:</label>
            <select
              id="logs-source-filter"
              name="selectedSource"
              aria-label="Filter logs by source"
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">ALL SOURCES</option>
              <option value="WindowsEvent">WindowsEvent</option>
              <option value="LinuxSyslog">LinuxSyslog</option>
              <option value="Firewall">Firewall</option>
              <option value="EndpointEDR">EndpointEDR</option>
              <option value="AWSCloudTrail">AWSCloudTrail</option>
            </select>
          </div>

          <label htmlFor="logs-anomaly-only-checkbox" className="flex items-center space-x-2 cursor-pointer select-none">
            <input
              id="logs-anomaly-only-checkbox"
              name="anomalyOnly"
              type="checkbox"
              checked={anomalyOnly}
              onChange={(e) => setAnomalyOnly(e.target.checked)}
              className="rounded bg-soc-bg border-soc-border text-cyan-500 focus:ring-cyan-500"
            />
            <span className="text-red-400 font-semibold">ANOMALIES ONLY</span>
          </label>
        </div>

        <div className="text-slate-400">
          Showing <span className="text-cyan-400 font-bold">{filteredLogs.length}</span> of {logs.length} events
        </div>
      </div>

      <LogTable logs={filteredLogs} />
    </div>
  );
};
