import React from 'react';
import { useSOC } from '../context/SOCContext';
import { MetricCard } from '../components/MetricCard';
import { LogTable } from '../components/LogTable';
import { AlertCard } from '../components/AlertCard';
import { ThreatMap } from '../components/ThreatMap';
import { ShieldAlert, Terminal, AlertOctagon, Activity, Zap, Cpu, Clock, Timer } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { logs, alerts, analytics } = useSOC();
  const navigate = useNavigate();

  const metrics = analytics?.metrics;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Total Event Logs"
          value={metrics?.total_logs ?? 0}
          subtext="Normalized log streams"
          icon={Terminal}
          color="cyan"
        />
        <MetricCard
          title="ML Anomalies"
          value={metrics?.anomalous_logs ?? 0}
          subtext="Isolation Forest > 65"
          icon={Cpu}
          color="amber"
        />
        <MetricCard
          title="Critical Alerts"
          value={metrics?.critical_alerts ?? 0}
          subtext="Immediate triage"
          icon={ShieldAlert}
          color="red"
        />
        <MetricCard
          title="Active Incidents"
          value={metrics?.open_incidents ?? 0}
          subtext="Correlated cases"
          icon={AlertOctagon}
          color="purple"
        />
        <MetricCard
          title="MTTD (Detect Time)"
          value={`${metrics?.mttd_seconds ?? 12.5}s`}
          subtext="Automated ML correlation"
          icon={Clock}
          color="cyan"
        />
        <MetricCard
          title="MTTR (Respond Time)"
          value={`${metrics?.mttr_seconds ?? 320.0}s`}
          subtext="Automated playbook SOAR"
          icon={Timer}
          color="emerald"
        />
      </div>

      {/* Main Grid: Attack Map & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <ThreatMap />

          {/* Live Log Stream Table */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                Live Ingested Log Stream
              </h3>
              <button
                onClick={() => navigate('/logs')}
                className="text-xs font-mono text-cyan-400 hover:underline"
              >
                View All Logs →
              </button>
            </div>
            <LogTable logs={logs.slice(0, 5)} />
          </div>
        </div>

        {/* Right Column: SIEM Security Alert Feed & Copilot Banner */}
        <div className="space-y-6">
          {/* Copilot Quick Launch Card */}
          <div className="p-5 rounded-xl border border-cyan-800/60 bg-gradient-to-br from-cyan-950/60 to-slate-900 glass-panel space-y-3">
            <div className="flex items-center space-x-2 text-cyan-400 font-mono text-xs font-semibold">
              <Zap className="h-4 w-4" />
              <span>10-POINT EVIDENCE COPILOT ACTIVE</span>
            </div>
            <p className="text-xs text-slate-300">
              Copilot correlates Isolation Forest score, transparent risk factors, and empirical telemetry evidence.
            </p>
            <button
              onClick={() => navigate('/copilot')}
              className="w-full py-2 px-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20"
            >
              <span>Launch Security Copilot</span>
              <Cpu className="h-4 w-4" />
            </button>
          </div>

          {/* Active Security Alerts */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-red-400" />
                SIEM Alert Queue
              </h3>
              <span className="text-xs font-mono text-slate-400">{alerts.length} Active</span>
            </div>

            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {alerts.slice(0, 4).map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onSelectCopilot={() => navigate('/copilot')}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
