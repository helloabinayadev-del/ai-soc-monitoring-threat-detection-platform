import React, { useEffect, useState } from 'react';
import { FileText, RefreshCw, Filter, ShieldCheck, AlertCircle } from 'lucide-react';
import { auditApi } from '../services/api';
import { AuditLogItem } from '../types';
import { formatTimestamp } from '../utils/formatDate';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('ALL');

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const data = await auditApi.getAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error('[!] Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (actionFilter !== 'ALL' && log.action !== actionFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6 pb-12 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="h-5 w-5 text-cyan-400" />
            Security Operations Audit Trail
          </h2>
          <p className="text-xs text-slate-400">
            Immutable system audit logs tracking analyst logins, log ingestions, containment actions, and ticket updates.
          </p>
        </div>

        <button
          onClick={fetchAuditLogs}
          disabled={loading}
          className="px-3 py-2 rounded-lg bg-soc-card border border-soc-border hover:border-slate-600 text-slate-300 transition flex items-center space-x-2 text-xs"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl border border-soc-border bg-soc-card/90 glass-panel flex items-center justify-between gap-4 text-xs">
        <div className="flex items-center space-x-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <label htmlFor="audit-action-filter" className="text-slate-400">ACTION TYPE:</label>
          <select
            id="audit-action-filter"
            name="actionFilter"
            aria-label="Filter audit logs by action type"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-soc-bg border border-soc-border rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">ALL ACTIONS</option>
            <option value="LOGIN">LOGIN</option>
            <option value="LOG_INGEST">LOG_INGEST</option>
            <option value="CONTAINMENT_ACTION">CONTAINMENT_ACTION</option>
            <option value="INCIDENT_CREATE">INCIDENT_CREATE</option>
          </select>
        </div>

        <div className="text-slate-400">
          Total Audit Records: <span className="text-cyan-400 font-bold">{filteredLogs.length}</span>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl border border-soc-border bg-soc-card/90 glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-soc-border text-slate-400">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">TIMESTAMP</th>
                <th className="p-3">ACTOR</th>
                <th className="p-3">ACTION</th>
                <th className="p-3">RESOURCE</th>
                <th className="p-3">STATUS</th>
                <th className="p-3">DETAILS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-cyan-400">
                    Loading security audit logs...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No audit records found matching criteria.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-soc-hover/50 transition">
                    <td className="p-3 font-semibold text-slate-400">#{log.id}</td>
                    <td className="p-3 text-slate-400 whitespace-nowrap">{formatTimestamp(log.timestamp)}</td>
                    <td className="p-3 text-cyan-400 font-bold">{log.actor_username}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
                        {log.action}
                      </span>
                    </td>
                    <td className="p-3 text-slate-400">
                      {log.resource_type ? `${log.resource_type} (${log.resource_id || 'N/A'})` : '—'}
                    </td>
                    <td className="p-3">
                      {log.status === 'SUCCESS' ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                          <ShieldCheck className="h-3.5 w-3.5" /> SUCCESS
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-red-400 font-bold">
                          <AlertCircle className="h-3.5 w-3.5" /> {log.status}
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-slate-400 max-w-xs truncate">{log.details || '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
