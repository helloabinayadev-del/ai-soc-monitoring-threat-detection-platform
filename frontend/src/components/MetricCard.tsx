import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  trend?: string;
  color?: 'cyan' | 'red' | 'amber' | 'emerald' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  trend,
  color = 'cyan',
}) => {
  const colorStyles = {
    cyan: 'text-cyan-400 bg-cyan-950/40 border-cyan-800/40 glow-border-cyan',
    red: 'text-red-400 bg-red-950/40 border-red-800/40 glow-border-red',
    amber: 'text-amber-400 bg-amber-950/40 border-amber-800/40 glow-border-amber',
    emerald: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40',
    purple: 'text-purple-400 bg-purple-950/40 border-purple-800/40',
  };

  return (
    <div className={`p-5 rounded-xl border ${colorStyles[color]} glass-panel transition hover:scale-[1.01]`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg ${colorStyles[color].split(' ')[1]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold font-mono tracking-tight text-slate-100">{value}</span>
        {trend && (
          <span className="text-xs font-mono text-cyan-400 font-medium">{trend}</span>
        )}
      </div>
      {subtext && <p className="mt-1 text-[11px] text-slate-500">{subtext}</p>}
    </div>
  );
};
