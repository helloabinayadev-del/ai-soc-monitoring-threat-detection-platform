import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldAlert, 
  Lock, 
  User as UserIcon, 
  ArrowRight, 
  Eye, 
  EyeOff, 
  Loader2, 
  ShieldCheck 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

export const LoginPage: React.FC = () => {
  const { isAuthenticated, isLoading, login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Auto-redirect to Dashboard if user is already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading && isAuthenticated) {
    return (
      <div className="min-h-screen bg-soc-bg flex items-center justify-center text-cyan-400 font-mono text-xs">
        Initializing AI SOC Platform session...
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Please enter both username and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await authApi.login(username.trim(), password);
      login(data.access_token, data.user);
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      if (!err.response) {
        setError('Connection to the SOC service was lost. Check the backend and try again.');
      } else if (err.response.status === 401) {
        setError('Invalid username or password.');
      } else if (err.response.status === 403) {
        setError('Access denied. Account is disabled or lacks required security clearance.');
      } else if (err.response.status === 422) {
        setError('Invalid input format. Please check your username and password.');
      } else if (err.response.status >= 500) {
        setError('Unable to connect to the security service. Please try again.');
      } else {
        setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-soc-bg text-slate-100 flex items-center justify-center p-4 sm:p-6 relative overflow-hidden font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Background Subtle Cyber Grid & Ambient Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(#1E293B_1px,transparent_1px)] [background-size:32px_32px] opacity-25 pointer-events-none"></div>
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/3 right-1/3 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* SINGLE CENTERED LOGIN CARD */}
      <div className="w-full max-w-md glass-panel p-8 sm:p-10 rounded-2xl border border-soc-border shadow-2xl relative z-10 space-y-6">
        
        {/* Branding Header (Inside Card) */}
        <div className="text-center space-y-2">
          <div className="mx-auto h-14 w-14 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <ShieldAlert className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight text-white font-sans">
            AI SOC PLATFORM
          </h1>
          <p className="text-xs text-cyan-400 font-mono font-medium tracking-wide uppercase">
            Enterprise Threat Detection & Monitoring Portal
          </p>
        </div>

        {/* Card Subheader */}
        <div className="text-center border-t border-soc-border/60 pt-4 space-y-1">
          <h2 className="text-lg font-bold text-slate-100 font-sans">
            Welcome back
          </h2>
          <p className="text-xs text-slate-400 font-sans">
            Sign in to access the Security Operations Center.
          </p>
        </div>

        {/* Error Alert Message */}
        {error && (
          <div
            id="login-error-alert"
            role="alert"
            className="p-3.5 rounded-lg bg-red-950/90 border border-red-800 text-red-400 text-xs font-mono space-y-1"
          >
            <div className="font-semibold flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-red-400 shrink-0" />
              <span>Authentication Failure</span>
            </div>
            <p className="text-[11px] leading-relaxed text-red-300">{error}</p>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-5 font-sans" noValidate>
          
          {/* Username Input */}
          <div>
            <label 
              htmlFor="username-input" 
              className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono"
            >
              Username
            </label>
            <div className="relative">
              <UserIcon className="absolute left-3.5 top-3 h-4 w-4 text-slate-500 pointer-events-none" />
              <input
                id="username-input"
                name="username"
                type="text"
                required
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full pl-10 pr-4 py-2.5 bg-soc-bg border border-soc-border rounded-lg text-slate-100 placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
              />
            </div>
          </div>

          {/* Password Input with Show/Hide Toggle */}
          <div>
            <label 
              htmlFor="password-input" 
              className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono"
            >
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-500 pointer-events-none" />
              <input
                id="password-input"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full pl-10 pr-10 py-2.5 bg-soc-bg border border-soc-border rounded-lg text-slate-100 placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 p-1 text-slate-500 hover:text-slate-300 focus:outline-none rounded"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-slate-400" />
                ) : (
                  <Eye className="h-4 w-4 text-slate-400" />
                )}
              </button>
            </div>
          </div>

          {/* Sign-In Submit Button */}
          <button
            id="login-submit-button"
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-soc-bg"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-white" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        {/* Trust & Security Indicator */}
        <div className="pt-4 border-t border-soc-border/60 text-center">
          <div className="inline-flex items-center space-x-2 text-[11px] font-mono text-slate-400">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
            <span>Protected Security Operations Environment</span>
          </div>
        </div>

      </div>
    </div>
  );
};
