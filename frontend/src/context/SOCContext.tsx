import React, { createContext, useContext, useState, useEffect } from 'react';
import { LogEvent, SecurityAlert, AnalyticsSummary } from '../types';
import { logsApi, alertsApi, analyticsApi } from '../services/api';
import { socWebSocket } from '../services/websocket';

interface SOCContextType {
  logs: LogEvent[];
  alerts: SecurityAlert[];
  analytics: AnalyticsSummary | null;
  refreshData: () => Promise<void>;
  isLoading: boolean;
}

const SOCContext = createContext<SOCContextType | undefined>(undefined);

export const SOCProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshData = async () => {
    try {
      const [logsData, alertsData, analyticsData] = await Promise.all([
        logsApi.getLogs({ limit: 50 }),
        alertsApi.getAlerts({ limit: 30 }),
        analyticsApi.getSummary(),
      ]);
      setLogs(logsData);
      setAlerts(alertsData);
      setAnalytics(analyticsData);
    } catch (e) {
      console.error('[!] Failed to load SOC context telemetry data:', e);
      throw e;
    } finally {
      setIsLoading(false);
    }
  };


  useEffect(() => {
    refreshData();
    socWebSocket.connect();

    const unsubscribe = socWebSocket.subscribe((msg) => {
      if (msg.type === 'NEW_LOG') {
        refreshData();
      } else if (msg.type === 'NEW_ALERT') {
        refreshData();
      }
    });

    return () => unsubscribe();
  }, []);

  return (
    <SOCContext.Provider value={{ logs, alerts, analytics, refreshData, isLoading }}>
      {children}
    </SOCContext.Provider>
  );
};

export const useSOC = () => {
  const context = useContext(SOCContext);
  if (!context) throw new Error('useSOC must be used within SOCProvider');
  return context;
};
