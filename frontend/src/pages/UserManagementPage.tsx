import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Search, Filter, ShieldCheck, ShieldAlert, KeyRound, CheckCircle2, XCircle, RefreshCw, Edit } from 'lucide-react';
import { User } from '../types';
import { authApi } from '../services/api';
import { formatTimestamp } from '../utils/formatDate';

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters & Search
  const [search, setSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Modals state
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<User | null>(null);
  const [showResetPwdModal, setShowResetPwdModal] = useState<User | null>(null);

  // Create Form State
  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    full_name: '',
    role: 'SOC_ANALYST',
    password: ''
  });

  // Edit Form State
  const [editForm, setEditForm] = useState({
    full_name: '',
    role: 'SOC_ANALYST',
    is_active: true
  });

  // Password Reset State
  const [newPassword, setNewPassword] = useState<string>('');

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await authApi.getUsers({
        search: search.trim() || undefined,
        role: roleFilter !== 'ALL' ? roleFilter : undefined,
        is_active: statusFilter === 'ACTIVE' ? true : statusFilter === 'INACTIVE' ? false : undefined
      });
      setUsers(data);
    } catch (err: any) {
      console.error('[!] Error loading users:', err);
      setError(err.response?.data?.detail || 'Failed to load platform users.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [search, roleFilter, statusFilter]);

  const showFeedback = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(null), 4000);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authApi.createUser(createForm);
      setShowCreateModal(false);
      setCreateForm({ username: '', email: '', full_name: '', role: 'SOC_ANALYST', password: '' });
      showFeedback(`Successfully created user '${createForm.username}'`);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create user.');
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showEditModal) return;
    try {
      await authApi.updateUser(showEditModal.id, editForm);
      setShowEditModal(null);
      showFeedback(`Updated profile for '${showEditModal.username}'`);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update user.');
    }
  };

  const handleToggleStatus = async (user: User) => {
    try {
      const updated = await authApi.toggleUserStatus(user.id, !user.is_active);
      showFeedback(`User '${user.username}' is now ${updated.is_active ? 'ACTIVE' : 'DEACTIVATED'}`);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to change user status.');
    }
  };

  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showResetPwdModal) return;
    try {
      await authApi.resetPassword(showResetPwdModal.id, newPassword);
      setShowResetPwdModal(null);
      setNewPassword('');
      showFeedback(`Password reset successfully for '${showResetPwdModal.username}'`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reset password.');
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Users className="h-5 w-5 text-cyan-400" />
            User & Role Administration
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Manage SOC platform user accounts, role-based access control (RBAC), and authentication credentials.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold font-mono rounded-lg flex items-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer self-start sm:self-auto"
        >
          <UserPlus className="h-4 w-4" />
          Create New SOC User
        </button>
      </div>

      {/* Success Notification Banner */}
      {successMessage && (
        <div className="p-3 rounded-lg border border-emerald-800 bg-emerald-950/80 text-emerald-300 text-xs font-mono flex items-center justify-between">
          <span>✓ {successMessage}</span>
          <button onClick={() => setSuccessMessage(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Search & Filters */}
      <div className="p-4 rounded-xl border border-soc-border bg-soc-card/90 glass-panel flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            id="user-search-input"
            name="userSearch"
            type="text"
            autoComplete="off"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by username, email, name..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-soc-bg border border-soc-border rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        {/* Role & Status Filters */}
        <div className="flex items-center space-x-3 w-full sm:w-auto font-mono text-xs">
          <div className="flex items-center space-x-1">
            <Filter className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-slate-400 text-[10px]">ROLE:</span>
            <select
              id="user-role-filter"
              name="roleFilter"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded p-1.5 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Roles</option>
              <option value="SOC_ADMIN">SOC_ADMIN (Admin)</option>
              <option value="SOC_ANALYST">SOC_ANALYST (Analyst)</option>
              <option value="INCIDENT_RESPONDER">INCIDENT_RESPONDER</option>
              <option value="SECURITY_VIEWER">SECURITY_VIEWER (Viewer)</option>
            </select>
          </div>

          <div className="flex items-center space-x-1">
            <span className="text-slate-400 text-[10px]">STATUS:</span>
            <select
              id="user-status-filter"
              name="statusFilter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded p-1.5 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Status</option>
              <option value="ACTIVE">Active Only</option>
              <option value="INACTIVE">Deactivated Only</option>
            </select>
          </div>

          <button
            onClick={fetchUsers}
            className="p-1.5 rounded border border-soc-border bg-soc-bg text-slate-400 hover:text-cyan-400"
            title="Refresh Users"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl border border-red-800 bg-red-950/60 text-red-300 text-xs font-mono">
          ✕ {error}
        </div>
      )}

      {/* Users Table */}
      <div className="rounded-xl border border-soc-border bg-soc-card/90 glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-soc-bg border-b border-soc-border text-slate-400 text-[10px] uppercase">
              <tr>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Assigned Role</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Last Login</th>
                <th className="py-3 px-4">Created Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-cyan-400 text-xs">
                    Loading platform user accounts...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 text-xs">
                    No matching users found.
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const isAdmin = u.role === 'SOC_ADMIN' || u.role === 'Admin';
                  const isAnalyst = u.role === 'SOC_ANALYST' || u.role === 'Analyst';
                  const isResponder = u.role === 'INCIDENT_RESPONDER' || u.role === 'Responder';

                  return (
                    <tr key={u.id} className="hover:bg-soc-hover/60 transition">
                      {/* User details */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-cyan-400 text-xs">
                            {u.username.substring(0, 2).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-bold text-slate-100">{u.full_name || u.username}</div>
                            <div className="text-[10px] text-slate-400">{u.email} • @{u.username}</div>
                          </div>
                        </div>
                      </td>

                      {/* Role */}
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${
                            isAdmin
                              ? 'bg-purple-950 text-purple-300 border-purple-800'
                              : isAnalyst
                              ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                              : isResponder
                              ? 'bg-amber-950 text-amber-300 border-amber-800'
                              : 'bg-slate-800 text-slate-300 border-slate-700'
                          }`}
                        >
                          {u.role}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        {u.is_active ? (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold flex items-center gap-1 w-max">
                            <CheckCircle2 className="h-3 w-3" /> ACTIVE
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-red-950 text-red-400 border border-red-800 font-bold flex items-center gap-1 w-max">
                            <XCircle className="h-3 w-3" /> DEACTIVATED
                          </span>
                        )}
                      </td>

                      {/* Dates */}
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {u.last_login ? formatTimestamp(u.last_login) : 'Never'}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {formatTimestamp(u.created_at)}
                      </td>

                      {/* Action buttons */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {
                              setShowEditModal(u);
                              setEditForm({ full_name: u.full_name || '', role: u.role, is_active: u.is_active });
                            }}
                            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                            title="Edit Role / Profile"
                          >
                            <Edit className="h-3.5 w-3.5" />
                          </button>

                          <button
                            onClick={() => setShowResetPwdModal(u)}
                            className="p-1.5 rounded bg-slate-800 hover:bg-amber-950 hover:text-amber-400 text-slate-300"
                            title="Reset Password"
                          >
                            <KeyRound className="h-3.5 w-3.5" />
                          </button>

                          <button
                            onClick={() => handleToggleStatus(u)}
                            className={`px-2 py-1 rounded text-[10px] font-bold ${
                              u.is_active
                                ? 'bg-red-950 hover:bg-red-900 text-red-400 border border-red-800'
                                : 'bg-emerald-950 hover:bg-emerald-900 text-emerald-400 border border-emerald-800'
                            }`}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE USER MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-md p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <UserPlus className="h-5 w-5 text-cyan-400" /> Create New Platform User
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-3">
              <div>
                <label htmlFor="create-email-input" className="block text-slate-400 mb-1">Email Address *</label>
                <input
                  id="create-email-input"
                  name="createEmail"
                  type="email"
                  required
                  autoComplete="off"
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  placeholder="analyst@enterprise.com"
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label htmlFor="create-username-input" className="block text-slate-400 mb-1">Username *</label>
                <input
                  id="create-username-input"
                  name="createUsername"
                  type="text"
                  required
                  autoComplete="off"
                  value={createForm.username}
                  onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                  placeholder="j.smith"
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label htmlFor="create-fullname-input" className="block text-slate-400 mb-1">Full Name</label>
                <input
                  id="create-fullname-input"
                  name="createFullName"
                  type="text"
                  autoComplete="off"
                  value={createForm.full_name}
                  onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })}
                  placeholder="John Smith"
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label htmlFor="create-role-select" className="block text-slate-400 mb-1">Assign Role *</label>
                <select
                  id="create-role-select"
                  name="createRole"
                  value={createForm.role}
                  onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="SOC_ADMIN">SOC_ADMIN (Full Admin Access)</option>
                  <option value="SOC_ANALYST">SOC_ANALYST (Triage & Triage Features)</option>
                  <option value="INCIDENT_RESPONDER">INCIDENT_RESPONDER (Incident Containment)</option>
                  <option value="SECURITY_VIEWER">SECURITY_VIEWER (Read-Only Dashboards)</option>
                </select>
              </div>

              <div>
                <label htmlFor="create-password-input" className="block text-slate-400 mb-1">Initial Password *</label>
                <input
                  id="create-password-input"
                  name="createPassword"
                  type="password"
                  required
                  autoComplete="new-password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  placeholder="••••••••••••"
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold"
                >
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT USER MODAL */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-md p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Edit className="h-5 w-5 text-cyan-400" /> Edit User Profile: @{showEditModal.username}
              </h3>
              <button onClick={() => setShowEditModal(null)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-3">
              <div>
                <label htmlFor="edit-fullname-input" className="block text-slate-400 mb-1">Full Name</label>
                <input
                  id="edit-fullname-input"
                  name="editFullName"
                  type="text"
                  autoComplete="off"
                  value={editForm.full_name}
                  onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label htmlFor="edit-role-select" className="block text-slate-400 mb-1">Assigned Role</label>
                <select
                  id="edit-role-select"
                  name="editRole"
                  value={editForm.role}
                  onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="SOC_ADMIN">SOC_ADMIN (Full Admin Access)</option>
                  <option value="SOC_ANALYST">SOC_ANALYST (Triage & Incident Operations)</option>
                  <option value="INCIDENT_RESPONDER">INCIDENT_RESPONDER (Incident Operations)</option>
                  <option value="SECURITY_VIEWER">SECURITY_VIEWER (Read-Only)</option>
                </select>
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditModal(null)}
                  className="px-4 py-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESET PASSWORD MODAL */}
      {showResetPwdModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-md p-6 space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <KeyRound className="h-5 w-5 text-amber-400" /> Reset Password: @{showResetPwdModal.username}
              </h3>
              <button onClick={() => setShowResetPwdModal(null)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>

            <form onSubmit={handleResetPasswordSubmit} className="space-y-3">
              <div>
                <label htmlFor="reset-password-input" className="block text-slate-400 mb-1">New Secure Password *</label>
                <input
                  id="reset-password-input"
                  name="newPassword"
                  type="password"
                  required
                  autoComplete="new-password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password..."
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowResetPwdModal(null)}
                  className="px-4 py-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-amber-600 hover:bg-amber-500 text-white font-bold"
                >
                  Reset Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
