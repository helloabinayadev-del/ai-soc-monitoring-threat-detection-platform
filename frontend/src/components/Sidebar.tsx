import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Terminal, 
  ShieldAlert, 
  AlertTriangle, 
  Globe2, 
  Bot, 
  BarChart3, 
  Settings,
  FileText,
  Users,
  X
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  adminOnly?: boolean;
}

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onMobileClose }) => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'SOC_ADMIN' || user?.role === 'Admin';

  const navItems: NavItem[] = [
    { name: 'SOC Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Live Event Logs', path: '/logs', icon: Terminal },
    { name: 'SIEM Alerts', path: '/alerts', icon: ShieldAlert },
    { name: 'Incident Response', path: '/incidents', icon: AlertTriangle },
    { name: 'Threat Intelligence', path: '/threat-intel', icon: Globe2 },
    { name: 'AI Security Copilot', path: '/copilot', icon: Bot },
    { name: 'Metrics & Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Security Audit Trail', path: '/audit', icon: FileText },
    ...(isAdmin ? [{ name: 'User Management', path: '/users', icon: Users, adminOnly: true }] : []),
    { name: 'Settings & Rules', path: '/settings', icon: Settings },
  ];


  const content = (
    <div className="flex flex-col justify-between h-full py-6 px-3">
      <div className="space-y-1">
        <div className="flex items-center justify-between px-3 pb-3">
          <span className="text-[10px] font-mono font-semibold text-slate-500 uppercase tracking-wider">
            SOC Navigation
          </span>
          {onMobileClose && (
            <button onClick={onMobileClose} className="md:hidden text-slate-400 hover:text-slate-200">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onMobileClose}
              className={({ isActive }: { isActive: boolean }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-950 to-slate-900 text-cyan-400 border-l-2 border-cyan-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-soc-hover'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-4 w-4" />
                <span>{item.name}</span>
              </div>
            </NavLink>
          );
        })}
      </div>

      {/* Footer System Status Indicator */}
      <div className="p-4 m-1 rounded-lg border border-soc-border bg-soc-bg/60 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-mono text-[10px]">CORRELATION ENGINE</span>
          <span className="text-[10px] text-emerald-400 font-mono">ONLINE</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div className="bg-cyan-500 h-1.5 rounded-full w-full animate-pulse"></div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside className="w-64 border-r border-soc-border bg-soc-card/70 backdrop-blur-md hidden md:flex flex-col min-h-[calc(100vh-4rem)]">
        {content}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onMobileClose}></div>
          <aside className="relative w-64 max-w-xs bg-soc-card border-r border-soc-border shadow-2xl flex flex-col z-50">
            {content}
          </aside>
        </div>
      )}
    </>
  );
};
