import React from 'react';
import { Shield, Server, Laptop, Flame, Activity } from 'lucide-react';

export const ThreatMap: React.FC = () => {
  const nodes = [
    { id: '1', name: 'Boundary Firewall', type: 'firewall', status: 'CRITICAL', ip: '198.51.100.45', x: 15, y: 30 },
    { id: '2', name: 'DC-PRIMARY-01', type: 'server', status: 'CRITICAL', ip: '10.0.2.88', x: 50, y: 20 },
    { id: '3', name: 'SRV-APP-PROD01', type: 'server', status: 'HIGH', ip: '10.0.4.12', x: 50, y: 70 },
    { id: '4', name: 'WKSTn-HR-09', type: 'laptop', status: 'HIGH', ip: '10.0.1.50', x: 80, y: 35 },
    { id: '5', name: 'WKSTn-FIN-02', type: 'laptop', status: 'NORMAL', ip: '192.168.1.105', x: 80, y: 75 },
  ];

  return (
    <div className="p-5 rounded-xl border border-soc-border bg-soc-card/90 glass-panel">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            Infrastructure Threat Topology Map
          </h3>
          <p className="text-[11px] text-slate-400 font-mono">Live attack vector visualization & compromised assets</p>
        </div>
        <div className="flex items-center space-x-3 text-[10px] font-mono">
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-red-500"></span> Compromised</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-amber-500"></span> High Risk</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500"></span> Protected</span>
        </div>
      </div>

      <div className="relative h-64 bg-slate-950/80 rounded-lg border border-soc-border overflow-hidden p-4">
        {/* SVG Attack Vectors */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <line x1="15%" y1="30%" x2="50%" y2="20%" stroke="#EF4444" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <line x1="50%" y1="20%" x2="50%" y2="70%" stroke="#F59E0B" strokeWidth="1.5" />
          <line x1="15%" y1="30%" x2="80%" y2="35%" stroke="#EF4444" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
          <line x1="50%" y1="70%" x2="80%" y2="75%" stroke="#10B981" strokeWidth="1" />
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <div
            key={node.id}
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
            className="-translate-x-1/2 -translate-y-1/2 absolute flex flex-col items-center group cursor-pointer"
          >
            <div
              className={`p-3 rounded-xl border flex items-center justify-center shadow-lg transition transform group-hover:scale-110 ${
                node.status === 'CRITICAL'
                  ? 'bg-red-950/80 border-red-500 text-red-400 glow-border-red'
                  : node.status === 'HIGH'
                  ? 'bg-amber-950/80 border-amber-500 text-amber-400 glow-border-amber'
                  : 'bg-emerald-950/80 border-emerald-500 text-emerald-400'
              }`}
            >
              {node.type === 'firewall' && <Flame className="h-5 w-5" />}
              {node.type === 'server' && <Server className="h-5 w-5" />}
              {node.type === 'laptop' && <Laptop className="h-5 w-5" />}
            </div>
            <div className="mt-1 text-center font-mono">
              <div className="text-[11px] font-semibold text-slate-200">{node.name}</div>
              <div className="text-[9px] text-slate-400">{node.ip}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
