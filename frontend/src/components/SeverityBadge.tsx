import React from 'react';

interface SeverityBadgeProps {
  severity: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const sev = (severity || 'INFORMATIONAL').toUpperCase();

  const styles: Record<string, string> = {
    CRITICAL: 'bg-red-950 text-red-400 border-red-800 animate-pulse',
    HIGH: 'bg-red-900/60 text-red-300 border-red-700',
    MEDIUM: 'bg-amber-950 text-amber-400 border-amber-800',
    LOW: 'bg-blue-950 text-blue-400 border-blue-800',
    INFORMATIONAL: 'bg-slate-800 text-slate-400 border-slate-700',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold border uppercase tracking-wider ${
        styles[sev] || styles.INFORMATIONAL
      }`}
    >
      {sev}
    </span>
  );
};
