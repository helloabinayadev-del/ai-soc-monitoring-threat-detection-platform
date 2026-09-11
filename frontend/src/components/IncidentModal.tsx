import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { incidentsApi } from '../services/api';

interface IncidentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const IncidentModal: React.FC<IncidentModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [severity, setSeverity] = useState('HIGH');
  const [assignee, setAssignee] = useState('Senior Security Analyst');
  const [affectedSystems, setAffectedSystems] = useState('DC-PRIMARY-01, WKSTn-HR-09');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await incidentsApi.createIncident({
        title,
        summary,
        severity: severity as 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
        assignee,
        affected_systems: affectedSystems.split(',').map((s) => s.trim()),
        mitre_tactics: ['TA0002 - Execution', 'TA0004 - Privilege Escalation'],
      });
      onSuccess();
      onClose();
    } catch (err) {
      console.error('[!] Failed to create incident case:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-xl border border-soc-border bg-soc-card p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-soc-border pb-3">
          <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            Create Incident Response Ticket
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 font-mono text-xs">
          <div>
            <label htmlFor="incident-title-input" className="block text-slate-400 mb-1">INCIDENT TITLE</label>
            <input
              id="incident-title-input"
              name="title"
              type="text"
              required
              autoComplete="off"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Cobalt Strike Intrusion on DC-PRIMARY-01"
              className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label htmlFor="incident-summary-textarea" className="block text-slate-400 mb-1">EXECUTIVE SUMMARY</label>
            <textarea
              id="incident-summary-textarea"
              name="summary"
              required
              rows={3}
              autoComplete="off"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Provide context on initial vector and compromised assets..."
              className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="incident-severity-select" className="block text-slate-400 mb-1">SEVERITY</label>
              <select
                id="incident-severity-select"
                name="severity"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>

            <div>
              <label htmlFor="incident-assignee-input" className="block text-slate-400 mb-1">ASSIGNEE</label>
              <input
                id="incident-assignee-input"
                name="assignee"
                type="text"
                autoComplete="name"
                value={assignee}
                onChange={(e) => setAssignee(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="incident-affected-systems-input" className="block text-slate-400 mb-1">AFFECTED SYSTEMS (COMMA SEPARATED)</label>
            <input
              id="incident-affected-systems-input"
              name="affectedSystems"
              type="text"
              autoComplete="off"
              value={affectedSystems}
              onChange={(e) => setAffectedSystems(e.target.value)}
              className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="pt-3 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold"
            >
              {loading ? 'Creating...' : 'Create Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
