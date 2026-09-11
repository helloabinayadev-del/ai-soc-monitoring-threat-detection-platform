import React, { useState } from 'react';
import { useSOC } from '../context/SOCContext';
import { AlertCard } from '../components/AlertCard';
import { ShieldAlert, Filter, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const AlertsPage: React.FC = () => {
  const { alerts } = useSOC();
  const navigate = useNavigate();
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const filteredAlerts = alerts.filter((alert) => {
    if (severityFilter !== 'ALL' && alert.severity !== severityFilter) return false;
    if (statusFilter !== 'ALL' && alert.status !== statusFilter) return false;
    if (search && !alert.title.toLowerCase().includes(search.toLowerCase()) && !alert.rule_id.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-red-400" />
            SIEM Alert Queue & Rule Correlations
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Automated correlation rules, MITRE ATT&CK tactical mapping, and alert triage pipeline.
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="p-4 rounded-xl border border-soc-border bg-soc-card/90 glass-panel flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <label htmlFor="alerts-severity-filter" className="text-slate-400">SEVERITY:</label>
            <select
              id="alerts-severity-filter"
              name="severityFilter"
              aria-label="Filter alerts by severity"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">ALL SEVERITIES</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <label htmlFor="alerts-status-filter" className="text-slate-400">STATUS:</label>
            <select
              id="alerts-status-filter"
              name="statusFilter"
              aria-label="Filter alerts by status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">ALL STATUSES</option>
              <option value="NEW">NEW</option>
              <option value="INVESTIGATING">INVESTIGATING</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </div>
        </div>

        <div className="relative w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            id="alerts-search-input"
            name="alertSearch"
            type="text"
            autoComplete="off"
            aria-label="Search alerts by title or rule"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search alerts by title/rule..."
            className="w-full pl-9 pr-4 py-1.5 bg-soc-bg border border-soc-border rounded text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredAlerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onSelectCopilot={() => navigate('/copilot')}
          />
        ))}
      </div>
    </div>
  );
};
