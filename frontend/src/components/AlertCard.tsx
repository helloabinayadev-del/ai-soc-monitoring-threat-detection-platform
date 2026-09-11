import React, { useState } from 'react';
import { SecurityAlert } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { ShieldAlert, Cpu, Layers, Info, CheckCircle2, XCircle } from 'lucide-react';
import { alertsApi, feedbackApi } from '../services/api';
import { useSOC } from '../context/SOCContext';
import { formatTimestamp } from '../utils/formatDate';

interface AlertCardProps {
  alert: SecurityAlert;
  onSelectCopilot?: (alert: SecurityAlert) => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({ alert, onSelectCopilot }) => {
  const { refreshData } = useSOC();
  const [showFactors, setShowFactors] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);

  const handleStatusChange = async (newStatus: string) => {
    try {
      await alertsApi.updateStatus(alert.id, newStatus);
      refreshData();
    } catch (e) {
      console.error('[!] Failed to update alert status:', e);
    }
  };

  const handleFeedback = async (type: 'TRUE_POSITIVE' | 'FALSE_POSITIVE') => {
    try {
      await feedbackApi.submitFeedback({
        alert_id: alert.id,
        feedback_type: type,
        comments: `Analyst marked alert #${alert.id} as ${type}`
      });
      setFeedbackSent(type);
      refreshData();
    } catch (e) {
      console.error('[!] Failed to submit feedback:', e);
    }
  };

  const detectionBadgeColor = 
    alert.detection_source === 'HYBRID' ? 'bg-purple-950/80 text-purple-300 border-purple-800' :
    alert.detection_source === 'ML_ANOMALY' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' :
    'bg-blue-950/80 text-blue-300 border-blue-800';

  const priorityColor =
    alert.priority === 'CRITICAL' ? 'bg-red-950 text-red-400 border-red-800' :
    alert.priority === 'HIGH' ? 'bg-orange-950 text-orange-400 border-orange-800' :
    alert.priority === 'MEDIUM' ? 'bg-yellow-950 text-yellow-400 border-yellow-800' :
    'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <div className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel hover:border-cyan-500/50 transition space-y-3">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={alert.severity} />
            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${priorityColor}`}>
              Priority: {alert.priority || alert.severity}
            </span>
            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${detectionBadgeColor}`}>
              Src: {alert.detection_source || 'RULE_BASED'}
            </span>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
              {alert.rule_id}
            </span>
          </div>
          <h3 className="font-semibold text-sm text-slate-100 mt-2 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-red-400" />
            {alert.title}
          </h3>
        </div>

        <div className="text-right font-mono">
          <div className="text-xs text-slate-400 flex items-center justify-end gap-1">
            Risk Score
            <button 
              onClick={() => setShowFactors(!showFactors)} 
              className="text-cyan-400 hover:text-cyan-300"
              title="View transparent risk factors breakdown"
            >
              <Info className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="text-lg font-bold text-red-400">{alert.risk_score.toFixed(1)}</div>
          <div className="text-[10px] text-slate-500">{formatTimestamp(alert.created_at)}</div>
        </div>
      </div>

      <p className="text-xs text-slate-300 line-clamp-2">{alert.description}</p>

      {/* Risk Factors Explanation Drawer */}
      {showFactors && alert.risk_factors && alert.risk_factors.length > 0 && (
        <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-mono space-y-1">
          <div className="text-slate-400 font-bold mb-1">Transparent Risk Score Breakdown:</div>
          {alert.risk_factors.map((rf, idx) => (
            <div key={idx} className="flex items-center justify-between text-slate-300">
              <span>• {rf.factor}</span>
              <span className="text-cyan-400 font-semibold">+{rf.contribution} pts</span>
            </div>
          ))}
        </div>
      )}

      {/* Badges: MITRE & Correlation */}
      <div className="flex flex-wrap gap-2 text-[11px] font-mono">
        {alert.correlation_id && (
          <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 flex items-center gap-1">
            <Layers className="h-3 w-3" />
            {alert.correlation_id}
          </span>
        )}
        {alert.mitre_tactic && (
          <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
            {alert.mitre_tactic}
          </span>
        )}
        {alert.mitre_technique && (
          <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
            {alert.mitre_technique}
          </span>
        )}
        {alert.affected_asset && (
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
            Asset: {alert.affected_asset}
          </span>
        )}
      </div>

      {/* Footer Triage Controls & Feedback */}
      <div className="pt-3 border-t border-soc-border flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <label htmlFor={`alert-status-select-${alert.id}`} className="text-[11px] text-slate-500 font-mono">STATUS:</label>
          <select
            id={`alert-status-select-${alert.id}`}
            name="alertStatus"
            aria-label={`Update status for alert ${alert.id}`}
            value={alert.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="text-xs font-mono bg-soc-bg border border-soc-border rounded px-2 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="NEW">NEW</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
          </select>
        </div>

        {/* Analyst Feedback Controls */}
        <div className="flex items-center space-x-1 font-mono text-[11px]">
          <button
            onClick={() => handleFeedback('TRUE_POSITIVE')}
            disabled={feedbackSent !== null}
            className={`px-2 py-1 rounded border flex items-center gap-1 ${
              feedbackSent === 'TRUE_POSITIVE' 
                ? 'bg-emerald-950 text-emerald-400 border-emerald-700' 
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-emerald-400'
            }`}
            title="Mark as True Positive"
          >
            <CheckCircle2 className="h-3 w-3" />
            TP
          </button>

          <button
            onClick={() => handleFeedback('FALSE_POSITIVE')}
            disabled={feedbackSent !== null}
            className={`px-2 py-1 rounded border flex items-center gap-1 ${
              feedbackSent === 'FALSE_POSITIVE' 
                ? 'bg-red-950 text-red-400 border-red-700' 
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-red-400'
            }`}
            title="Mark as False Positive"
          >
            <XCircle className="h-3 w-3" />
            FP
          </button>
        </div>

        {onSelectCopilot && (
          <button
            onClick={() => onSelectCopilot(alert)}
            className="flex items-center space-x-1 px-3 py-1 rounded-lg bg-cyan-950 hover:bg-cyan-900 text-cyan-400 border border-cyan-800 text-xs font-medium transition"
          >
            <Cpu className="h-3.5 w-3.5" />
            <span>Copilot Analysis</span>
          </button>
        )}
      </div>
    </div>
  );
};
