import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Bell, Search, Activity, LogOut, Menu, CheckCircle2, CheckCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSOC } from '../context/SOCContext';
import { alertsApi } from '../services/api';

import { formatTimestamp } from '../utils/formatDate';

interface NavbarProps {
  onToggleMobileSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileSidebar }) => {
  const { user, logout } = useAuth();
  const { alerts, analytics, refreshData } = useSOC();
  const navigate = useNavigate();

  const [time, setTime] = useState<string>('');
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const popoverRef = useRef<HTMLDivElement>(null);

  // Live IST Clock
  useEffect(() => {
    const updateClock = () => {
      setTime(formatTimestamp(new Date()));
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  // Click outside & Esc key listeners
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const unreadAlerts = alerts.filter((a) => a.status === 'NEW' || a.status === 'INVESTIGATING');
  const threatLevel = analytics?.metrics.threat_level || 'ELEVATED';

  const handleMarkAsRead = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await alertsApi.updateStatus(id, 'RESOLVED');
      refreshData();
    } catch (err) {
      console.error('[!] Failed to mark alert as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await Promise.all(unreadAlerts.map((a) => alertsApi.updateStatus(a.id, 'RESOLVED')));
      refreshData();
    } catch (err) {
      console.error('[!] Failed to mark all as read:', err);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/logs?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="h-16 border-b border-soc-border bg-soc-card/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Left: Mobile Toggle & Brand */}
      <div className="flex items-center space-x-3">
        {onToggleMobileSidebar && (
          <button
            onClick={onToggleMobileSidebar}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-soc-hover"
            aria-label="Toggle Navigation Menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}

        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => navigate('/')}>
          <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldAlert className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-base sm:text-lg tracking-wide text-slate-100 flex items-center gap-2">
              AI SOC PLATFORM
              <span className="text-[10px] sm:text-xs font-mono font-medium px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                v1.0 ENTERPRISE
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              {time}
            </p>
          </div>
        </div>
      </div>

      {/* Middle: Global Threat Status Banner & Functional Search */}
      <div className="hidden lg:flex items-center space-x-6">
        <div className="flex items-center space-x-3 px-4 py-1.5 rounded-lg border border-soc-border bg-soc-bg">
          <Activity className="h-4 w-4 text-cyan-400 animate-spin" />
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">THREAT LEVEL:</span>
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${
              threatLevel === 'CRITICAL'
                ? 'bg-red-950 text-red-400 border border-red-800'
                : threatLevel === 'HIGH'
                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
            }`}
          >
            {threatLevel}
          </span>
        </div>

        <form onSubmit={handleSearchSubmit} className="relative w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400 pointer-events-none" />
          <input
            id="global-search-input"
            name="globalSearch"
            type="text"
            autoComplete="off"
            aria-label="Search IP, Host, User, Rule..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search IP, Host, User, Rule..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-soc-bg border border-soc-border rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </form>
      </div>

      {/* Right: Notification Popover & Profile Menu */}
      <div className="flex items-center space-x-4">
        {/* Notification Bell & Panel */}
        <div className="relative" ref={popoverRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-soc-hover border border-transparent hover:border-soc-border transition"
            title="Active Threat Notifications"
            aria-label="Threat Notifications"
          >
            <Bell className="h-5 w-5" />
            {unreadAlerts.length > 0 && (
              <span className="absolute top-1 right-1 h-2.5 w-2.5 rounded-full bg-red-500 ring-4 ring-soc-card animate-ping"></span>
            )}
            {unreadAlerts.length > 0 && (
              <span className="absolute top-1 right-1 h-2.5 w-2.5 rounded-full bg-red-500 ring-4 ring-soc-card"></span>
            )}
          </button>

          {/* Notifications Dropdown Panel */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-soc-card border border-soc-border rounded-xl shadow-2xl z-50 p-4 font-mono text-xs space-y-3">
              <div className="flex items-center justify-between border-b border-soc-border pb-2">
                <span className="font-bold text-slate-100 flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-red-400" />
                  THREAT NOTIFICATIONS ({unreadAlerts.length})
                </span>
                {unreadAlerts.length > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1"
                  >
                    <CheckCheck className="h-3.5 w-3.5" /> Mark All Read
                  </button>
                )}
              </div>

              <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                {alerts.length === 0 ? (
                  <div className="p-4 text-center text-slate-500">No active threat notifications.</div>
                ) : (
                  alerts.slice(0, 6).map((alert) => (
                    <div
                      key={alert.id}
                      onClick={() => {
                        setShowNotifications(false);
                        navigate('/alerts');
                      }}
                      className={`p-3 rounded-lg border transition cursor-pointer flex items-start justify-between ${
                        alert.status === 'NEW'
                          ? 'bg-red-950/40 border-red-800 text-slate-200'
                          : 'bg-slate-900/60 border-slate-800 text-slate-400'
                      }`}
                    >
                      <div className="space-y-1 pr-2">
                        <div className="flex items-center space-x-2">
                          <span className="px-1.5 py-0.5 rounded text-[9px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
                            {alert.rule_id}
                          </span>
                          <span className="text-[10px] text-red-400 font-bold">{alert.severity}</span>
                        </div>
                        <div className="font-semibold text-slate-100 text-[11px] line-clamp-1">{alert.title}</div>
                        <div className="text-[10px] text-slate-400">{formatTimestamp(alert.created_at)}</div>
                      </div>

                      {alert.status === 'NEW' && (
                        <button
                          onClick={(e) => handleMarkAsRead(alert.id, e)}
                          className="text-slate-400 hover:text-emerald-400 p-1"
                          title="Mark Resolved"
                        >
                          <CheckCircle2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>

              <div className="pt-2 border-t border-soc-border text-center">
                <button
                  onClick={() => {
                    setShowNotifications(false);
                    navigate('/alerts');
                  }}
                  className="text-[11px] text-cyan-400 hover:underline font-bold"
                >
                  View All SIEM Alerts Queue →
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-soc-border"></div>

        {/* User Profile & Logout */}
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-mono font-semibold text-cyan-400 text-xs">
            {user?.username?.substring(0, 2).toUpperCase() || 'SO'}
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-medium text-slate-200">{user?.full_name || user?.username}</div>
            <div className="text-[10px] text-cyan-400 font-mono">{user?.role || 'Analyst'}</div>
          </div>
          <button
            onClick={logout}
            title="Log Out Session"
            className="p-1.5 rounded hover:bg-red-950 hover:text-red-400 text-slate-400 transition"
            aria-label="Log Out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
