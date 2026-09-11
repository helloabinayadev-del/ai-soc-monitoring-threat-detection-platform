import React, { useState, useEffect } from 'react';
import { Incident, CorrelationGroup } from '../types';
import { incidentsApi, correlationsApi } from '../services/api';
import { IncidentModal } from '../components/IncidentModal';
import { AlertTriangle, Plus, ShieldCheck, CheckCircle2, User, Server, RefreshCw, Layers, GitMerge } from 'lucide-react';
import { SeverityBadge } from '../components/SeverityBadge';
import { formatTimestamp } from '../utils/formatDate';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [correlations, setCorrelations] = useState<CorrelationGroup[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'incidents' | 'correlations'>('incidents');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [incData, corrData] = await Promise.all([
        incidentsApi.getIncidents(),
        correlationsApi.getCorrelations()
      ]);
      setIncidents(incData);
      setCorrelations(corrData);
    } catch (e) {
      console.error('[!] Failed to load incident or correlation data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            Active Security Incidents & Correlation Engine
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Multi-stage attack pattern correlation, automated containment actions, and ticket management.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Tab Switcher */}
          <div className="flex items-center p-1 rounded-lg bg-soc-bg border border-soc-border text-xs font-mono">
            <button
              onClick={() => setActiveTab('incidents')}
              className={`px-3 py-1 rounded transition ${activeTab === 'incidents' ? 'bg-cyan-950 text-cyan-400 font-bold border border-cyan-800' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Incident Tickets ({incidents.length})
            </button>
            <button
              onClick={() => setActiveTab('correlations')}
              className={`px-3 py-1 rounded transition ${activeTab === 'correlations' ? 'bg-cyan-950 text-cyan-400 font-bold border border-cyan-800' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Correlation Chains ({correlations.length})
            </button>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center space-x-2 transition shadow-lg shadow-cyan-500/20"
          >
            <Plus className="h-4 w-4" />
            <span>New Ticket</span>
          </button>
          
          <button
            onClick={fetchData}
            className="p-2 rounded-lg bg-soc-card border border-soc-border hover:border-slate-600 text-slate-300 transition"
            title="Refresh Data"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {activeTab === 'correlations' ? (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-cyan-800/60 bg-cyan-950/40 font-mono text-xs text-cyan-200 flex items-center gap-3">
            <GitMerge className="h-5 w-5 text-cyan-400 shrink-0" />
            <div>
              <span className="font-bold">Multi-Stage Event Correlation Engine Active:</span> Security logs from the same source IP/host are automatically grouped into correlation chains with unique IDs (`CORR-YYYYMMDD-XXXX`).
            </div>
          </div>

          {correlations.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-mono text-xs">No active correlation chains found.</div>
          ) : (
            correlations.map((cg) => (
              <div key={cg.id} className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel space-y-3 font-mono">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-soc-border pb-3">
                  <div className="flex items-center space-x-3">
                    <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold text-xs">
                      {cg.correlation_id}
                    </span>
                    <span className="text-sm font-semibold text-slate-100">{cg.title}</span>
                    <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 text-xs">
                      {cg.event_count} Related Events
                    </span>
                  </div>

                  <div className="text-xs text-slate-400">
                    Risk: <span className="font-bold text-red-400">{cg.risk_score.toFixed(1)}/100</span> | Priority: <span className="font-bold text-amber-400">{cg.priority}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div><span className="text-slate-500">Source IP:</span> <span className="text-slate-200">{cg.source_ip || 'N/A'}</span></div>
                  <div><span className="text-slate-500">Target Asset:</span> <span className="text-slate-200">{cg.target_asset || 'N/A'}</span></div>
                  <div><span className="text-slate-500">First Observed:</span> <span className="text-slate-200">{formatTimestamp(cg.first_seen)}</span></div>
                </div>

                {cg.stage_summary && (
                  <div className="p-2 rounded bg-slate-950 text-slate-300 text-xs border border-slate-800">
                    <span className="text-slate-500 font-bold">Attack Progression Stage: </span>
                    <span className="text-purple-300">{cg.stage_summary}</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {loading ? (
            <div className="p-8 text-center text-cyan-400 font-mono text-xs">Loading incident tickets...</div>
          ) : incidents.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-mono text-xs">No active incident cases found.</div>
          ) : (
            incidents.map((inc) => (
              <div key={inc.id} className="p-6 rounded-xl border border-soc-border bg-soc-card/90 glass-panel space-y-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-soc-border pb-3">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                        {inc.incident_number}
                      </span>
                      <SeverityBadge severity={inc.severity} />
                      <span className="text-xs font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                        STATUS: {inc.status}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {formatTimestamp(inc.created_at)}
                      </span>
                    </div>
                    <h3 className="font-semibold text-base text-slate-100 mt-1">{inc.title}</h3>
                  </div>

                  <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
                    <User className="h-4 w-4 text-slate-500" />
                    <span>Assignee: {inc.assignee || 'Unassigned'}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 font-sans leading-relaxed">{inc.summary}</p>

                {/* Affected Assets & MITRE */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs pt-2">
                  <div className="p-3 rounded bg-slate-950/60 border border-slate-800 space-y-1">
                    <div className="text-[10px] text-slate-500 uppercase font-bold flex items-center gap-1">
                      <Server className="h-3.5 w-3.5 text-cyan-400" /> AFFECTED SYSTEMS & INFRASTRUCTURE
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {inc.affected_systems?.map((sys, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[11px]">
                          {sys}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 rounded bg-slate-950/60 border border-slate-800 space-y-1">
                    <div className="text-[10px] text-slate-500 uppercase font-bold flex items-center gap-1">
                      <ShieldCheck className="h-3.5 w-3.5 text-purple-400" /> MITRE ATT&CK TACTICAL CORRELATION
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {inc.mitre_tactics?.map((tac, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 text-[11px]">
                          {tac}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* AI Recommendation Banner & Automated Containment Action Controls */}
                {inc.ai_recommendation && (
                  <div className="p-3 rounded bg-cyan-950/40 border border-cyan-800 text-xs font-mono space-y-2 text-cyan-200">
                    <div className="font-bold text-cyan-400 flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4" /> AUTOMATED CONTAINMENT PLAYBOOK RECOMMENDATION:
                    </div>
                    <div>{inc.ai_recommendation}</div>

                    <div className="pt-2 flex flex-wrap gap-2">
                      <button
                        onClick={async () => {
                          try {
                            const res = await incidentsApi.executeContainmentAction(inc.id, 'ISOLATE_HOST');
                            alert(`[SIMULATED SOAR ACTION SUCCESS]: ${res.detail || 'EDR Host Isolation Executed'}`);
                            fetchData();
                          } catch (err) {
                            alert(`[!] Containment action failed: ${err}`);
                          }
                        }}
                        className="px-3 py-1 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 font-bold transition cursor-pointer"
                      >
                        Execute EDR Host Isolation
                      </button>
                      <button
                        onClick={async () => {
                          try {
                            const res = await incidentsApi.executeContainmentAction(inc.id, 'BLOCK_IP');
                            alert(`[SIMULATED SOAR ACTION SUCCESS]: ${res.detail || 'Firewall IP Blocking Executed'}`);
                            fetchData();
                          } catch (err) {
                            alert(`[!] Containment action failed: ${err}`);
                          }
                        }}
                        className="px-3 py-1 rounded bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-800 font-bold transition cursor-pointer"
                      >
                        Block Egress IP on Firewall
                      </button>
                      <button
                        onClick={async () => {
                          try {
                            const res = await incidentsApi.executeContainmentAction(inc.id, 'REVOKE_TOKENS');
                            alert(`[SIMULATED SOAR ACTION SUCCESS]: ${res.detail || 'User Session Tokens Revoked'}`);
                            fetchData();
                          } catch (err) {
                            alert(`[!] Containment action failed: ${err}`);
                          }
                        }}
                        className="px-3 py-1 rounded bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 font-bold transition cursor-pointer"
                      >
                        Revoke User Active Directory Tokens
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      <IncidentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  );
};
