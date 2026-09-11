import React, { useState } from 'react';
import { LogEvent } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { ChevronDown, ChevronRight, AlertOctagon, Terminal } from 'lucide-react';

import { formatTimestamp } from '../utils/formatDate';

interface LogTableProps {
  logs: LogEvent[];
}

export const LogTable: React.FC<LogTableProps> = ({ logs }) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-soc-border bg-soc-card/90">
      <table className="w-full text-left text-xs text-slate-300">
        <thead className="bg-soc-bg/80 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-soc-border">
          <tr>
            <th className="py-3 px-4 w-8"></th>
            <th className="py-3 px-4">Timestamp</th>
            <th className="py-3 px-4">Source</th>
            <th className="py-3 px-4">Event Type</th>
            <th className="py-3 px-4">Source IP → Dest IP</th>
            <th className="py-3 px-4">User / Host</th>
            <th className="py-3 px-4">Severity</th>
            <th className="py-3 px-4 text-right">Anomaly Score</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-soc-border font-mono">
          {logs.map((log) => {
            const isExpanded = expandedId === log.id;
            return (
              <React.Fragment key={log.id}>
                <tr
                  onClick={() => toggleExpand(log.id)}
                  className={`cursor-pointer transition hover:bg-soc-hover/80 ${
                    log.is_anomaly === 'ANOMALOUS' ? 'bg-red-950/20' : ''
                  }`}
                >
                  <td className="py-3 px-4">
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-cyan-400" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-slate-500" />
                    )}
                  </td>
                  <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                    {formatTimestamp(log.timestamp)}
                  </td>
                  <td className="py-3 px-4 font-semibold text-cyan-400 whitespace-nowrap">
                    {log.log_source}
                  </td>
                  <td className="py-3 px-4 text-slate-200">{log.event_type}</td>
                  <td className="py-3 px-4 text-slate-300 whitespace-nowrap">
                    {log.source_ip || 'N/A'}{' '}
                    <span className="text-slate-500">→</span>{' '}
                    {log.destination_ip || 'N/A'}
                  </td>
                  <td className="py-3 px-4 text-slate-300 whitespace-nowrap">
                    <span className="text-slate-100 font-semibold">{log.user_name || 'N/A'}</span>
                    <span className="text-slate-500 text-[10px] block">{log.hostname || 'N/A'}</span>
                  </td>
                  <td className="py-3 px-4">
                    <SeverityBadge severity={log.severity} />
                  </td>
                  <td className="py-3 px-4 text-right font-bold">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] ${
                        log.anomaly_score > 65
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      }`}
                    >
                      {log.anomaly_score.toFixed(1)}
                    </span>
                  </td>
                </tr>

                {/* Expanded Raw Payload View */}
                {isExpanded && (
                  <tr className="bg-slate-950/90 border-b border-cyan-900/50">
                    <td colSpan={8} className="p-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs font-mono text-cyan-400">
                          <span className="flex items-center gap-1.5">
                            <Terminal className="h-4 w-4" /> RAW LOG PAYLOAD
                          </span>
                          {log.is_anomaly === 'ANOMALOUS' && (
                            <span className="flex items-center gap-1 text-red-400 bg-red-950 px-2 py-0.5 rounded border border-red-800">
                              <AlertOctagon className="h-3.5 w-3.5" /> ISOLATION FOREST ANOMALY DETECTED
                            </span>
                          )}
                        </div>
                        <pre className="p-3 rounded bg-black/60 text-slate-300 text-xs font-mono overflow-x-auto border border-slate-800">
                          {log.raw_message}
                        </pre>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
