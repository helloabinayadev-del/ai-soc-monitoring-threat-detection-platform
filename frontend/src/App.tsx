import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SOCProvider } from './context/SOCContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { ProtectedRoute } from './components/ProtectedRoute';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { LogsPage } from './pages/LogsPage';
import { AlertsPage } from './pages/AlertsPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { ThreatIntelPage } from './pages/ThreatIntelPage';
import { CopilotPage } from './pages/CopilotPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { UserManagementPage } from './pages/UserManagementPage';

const ProtectedLayout: React.FC = () => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [mobileOpen, setMobileOpen] = React.useState<boolean>(false);
  const isAdmin = user?.role === 'SOC_ADMIN' || user?.role === 'Admin';

  if (isLoading) {
    return (
      <div className="min-h-screen bg-soc-bg flex items-center justify-center text-cyan-400 font-mono text-xs">
        Initializing AI SOC Platform session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <SOCProvider>
      <div className="min-h-screen bg-soc-bg flex flex-col">
        <Navbar onToggleMobileSidebar={() => setMobileOpen(!mobileOpen)} />
        <div className="flex flex-1">
          <Sidebar mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
          <main className="flex-1 p-4 sm:p-6 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/threat-intel" element={<ThreatIntelPage />} />
              <Route path="/threat-intelligence" element={<ThreatIntelPage />} />
              <Route path="/copilot" element={<CopilotPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/audit" element={<AuditLogsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route 
                path="/users" 
                element={isAdmin ? <UserManagementPage /> : <Navigate to="/dashboard" replace />} 
              />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </SOCProvider>
  );
};


export const App: React.FC = () => {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/*" element={<ProtectedLayout />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
