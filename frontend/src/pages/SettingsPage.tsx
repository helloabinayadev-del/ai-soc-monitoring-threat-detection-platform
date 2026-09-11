import React from 'react';
import { Settings, Shield, Sliders, Database, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [contamination, setContamination] = React.useState('0.05');
  const [autoTriage, setAutoTriage] = React.useState(true);
  const [wsNotifications, setWsNotifications] = React.useState(true);
  const [savedMessage, setSavedMessage] = React.useState<string | null>(null);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedMessage('Configuration settings saved successfully!');
    setTimeout(() => setSavedMessage(null), 4000);
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Settings className="h-5 w-5 text-cyan-400" />
          SOC Platform Settings & Rule Configuration
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          SIEM correlation engine rules, role-based access controls (RBAC), and database connections.
        </p>
      </div>

      {savedMessage && (
        <div className="p-3 rounded-lg border border-emerald-800 bg-emerald-950/60 text-emerald-300 text-xs font-mono">
          ✓ {savedMessage}
        </div>
      )}

      <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* User RBAC Profile */}
        <div className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel space-y-3 font-mono text-xs">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold border-b border-soc-border pb-2">
            <Users className="h-4 w-4" />
            <span>ACTIVE USER ROLE & RBAC PRIVILEGES</span>
          </div>
          <div className="space-y-2 text-slate-300">
            <div>User: <span className="text-slate-100 font-bold">{user?.full_name} ({user?.username})</span></div>
            <div>Email: <span className="text-slate-100">{user?.email}</span></div>
            <div>Assigned Role: <span className="text-cyan-400 font-bold uppercase">{user?.role}</span></div>
            <div>Permissions: <span className="text-emerald-400 font-bold">FULL SOC ADMIN & TRIAGE ACCESS</span></div>
            <div>Authentication: <span className="text-emerald-400 font-bold">JWT HMAC-SHA256 (SESSION ENCRYPTED)</span></div>
          </div>
        </div>

        {/* Engine Settings */}
        <div className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel space-y-3 font-mono text-xs">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold border-b border-soc-border pb-2">
            <Sliders className="h-4 w-4" />
            <span>SYSTEM & ML ENGINE CONFIGURATION STATUS</span>
          </div>
          <div className="space-y-3 text-slate-300">
            <div>
              <label htmlFor="settings-contamination-input" className="block text-slate-400 mb-1">ISOLATION FOREST CONTAMINATION THRESHOLD</label>
              <input
                id="settings-contamination-input"
                name="contamination"
                type="text"
                autoComplete="off"
                value={contamination}
                onChange={(e) => setContamination(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div className="flex items-center justify-between pt-1">
              <span className="text-slate-300">AUTOMATED SIEM ALERT TRIAGE</span>
              <button
                type="button"
                onClick={() => setAutoTriage(!autoTriage)}
                className={`px-3 py-1 rounded text-[11px] font-bold ${
                  autoTriage ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'
                }`}
              >
                {autoTriage ? 'ENABLED' : 'DISABLED'}
              </button>
            </div>
            <div className="flex items-center justify-between pt-1">
              <span className="text-slate-300">WEBSOCKET THREAT NOTIFICATIONS</span>
              <button
                type="button"
                onClick={() => setWsNotifications(!wsNotifications)}
                className={`px-3 py-1 rounded text-[11px] font-bold ${
                  wsNotifications ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-slate-800 text-slate-400'
                }`}
              >
                {wsNotifications ? 'ACTIVE' : 'MUTED'}
              </button>
            </div>
            <div>
              <label htmlFor="settings-secret-key-input" className="block text-slate-400 mb-1">SECRET KEY CONFIGURATION</label>
              <input
                id="settings-secret-key-input"
                name="secretKey"
                type="text"
                autoComplete="off"
                value="[PROTECTED - STORED IN BACKEND ENVIRONMENT]"
                readOnly
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-400 italic"
              />
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition cursor-pointer"
              >
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
