import React from 'react';
import { CopilotChat } from '../components/CopilotChat';
import { Bot, Sparkles, ShieldCheck, Cpu } from 'lucide-react';

export const CopilotPage: React.FC = () => {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Bot className="h-5 w-5 text-cyan-400" />
          AI Security Copilot & Interactive SOC Assistant
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          Contextual threat analysis, playbook synthesis, MITRE ATT&CK correlation, and automated incident triage.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <CopilotChat />
        </div>

        {/* Right Info Panel */}
        <div className="space-y-4 font-mono text-xs">
          <div className="p-4 rounded-xl border border-soc-border bg-soc-card space-y-2">
            <div className="flex items-center space-x-2 text-cyan-400 font-semibold">
              <Cpu className="h-4 w-4" />
              <span>COPILOT CAPABILITIES</span>
            </div>
            <ul className="list-disc list-inside text-slate-300 space-y-1.5 text-[11px] font-sans">
              <li>Log Anomaly & Isolation Forest Interpretation</li>
              <li>Automated Incident Containment Playbooks</li>
              <li>MITRE ATT&CK Tactic & Technique Extraction</li>
              <li>IOC Feed Correlation & VirusTotal Lookup</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl border border-purple-800/60 bg-purple-950/30 text-purple-200 space-y-2">
            <div className="flex items-center space-x-2 text-purple-300 font-semibold">
              <Sparkles className="h-4 w-4" />
              <span>ENGINE STATUS</span>
            </div>
            <div className="text-[11px]">
              Type: <span className="text-cyan-400 font-bold">Rule-Based / Heuristic SOC Engine</span>
            </div>
            <div className="text-[11px]">
              Pipeline: <span className="text-slate-300">FastAPI + scikit-learn IsolationForest Telemetry</span>
            </div>
            <div className="text-[11px]">
              Latency: <span className="text-emerald-400 font-bold">&lt; 20ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
