'use client';

import {useEffect, useState} from 'react';
import {motion} from 'framer-motion';
import {
  User,
  Lock,
  Bell,
  Key,
  Shield,
  Save,
  AlertCircle,
  CheckCircle,
  Eye,
  EyeOff,
  ChevronRight,
  Mail,
  Smartphone,
  Globe
} from 'lucide-react';
import {AppLayout} from '@/components/layout/AppLayout';
import {getUser, clearAuthData} from '@/lib/api/auth';
import {User as UserType} from '@/types/auth';

const settingsSections = [
  {id: 'profile', label: 'Profile', icon: User},
  {id: 'security', label: 'Security', icon: Shield},
  {id: 'notifications', label: 'Notifications', icon: Bell},
  {id: 'api', label: 'API Keys', icon: Key}
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('profile');
  const [, setUser] = useState<UserType | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [profileForm, setProfileForm] = useState({
    name: '',
    email: ''
  });

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    marketing: false,
    security: true
  });

  const [apiKeys, setApiKeys] = useState([
    {id: '1', name: 'Development', key: 'sk_dev_xxxxxxxxxxxx', createdAt: '2026-02-01', lastUsed: '2026-02-14'}
  ]);

  useEffect(() => {
    const currentUser = getUser();
    if (currentUser) {
      setUser(currentUser);
      setProfileForm({
        name: currentUser.name || '',
        email: currentUser.email || ''
      });
    }
  }, []);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    setMessage(null);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setMessage({type: 'success', text: 'Profile updated'});
    setIsSaving(false);
  };

  const handleChangePassword = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setMessage({type: 'error', text: 'Passwords do not match'});
      return;
    }
    if (passwordForm.newPassword.length < 8) {
      setMessage({type: 'error', text: 'Password must be at least 8 characters'});
      return;
    }
    setIsSaving(true);
    setMessage(null);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setMessage({type: 'success', text: 'Password changed'});
    setPasswordForm({currentPassword: '', newPassword: '', confirmPassword: ''});
    setIsSaving(false);
  };

  const handleGenerateApiKey = () => {
    const newKey = {
      id: Date.now().toString(),
      name: `API Key ${apiKeys.length + 1}`,
      key: `sk_live_${Math.random().toString(36).substring(2, 15)}`,
      createdAt: new Date().toISOString().split('T')[0],
      lastUsed: '-'
    };
    setApiKeys([...apiKeys, newKey]);
  };

  const handleDeleteApiKey = (id: string) => {
    if (!confirm('Delete this API key?')) { return; }
    setApiKeys(apiKeys.filter(k => k.id !== id));
  };

  const renderContent = () => {
    switch (activeSection) {
    case 'profile':
      return (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-[var(--color-text)] mb-4">Profile</h3>

            {message?.type === 'success' && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
                <CheckCircle className="w-5 h-5" />
                {message.text}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Display Name</label>
                <input
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({...profileForm, name: e.target.value})}
                  className="w-full px-4 py-2 bg-white border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Email</label>
                <input
                  type="email"
                  value={profileForm.email}
                  disabled
                  className="w-full px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-muted)] cursor-not-allowed"
                />
                <p className="mt-1 text-xs text-[var(--color-text-muted)]">Email cannot be changed</p>
              </div>

              <motion.button
                whileHover={{scale: 1.02}}
                whileTap={{scale: 0.98}}
                onClick={handleSaveProfile}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save Changes'}
              </motion.button>
            </div>
          </div>

          <div className="pt-6 border-t border-[var(--color-border)]">
            <h3 className="text-lg font-medium text-red-600 mb-4">Danger Zone</h3>
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700 mb-3">Deleting your account will permanently remove all data.</p>
              <button
                onClick={() => {
                  if (confirm('Are you sure? This cannot be undone!')) {
                    clearAuthData();
                    window.location.href = '/';
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
              >
                  Delete Account
              </button>
            </div>
          </div>
        </div>
      );

    case 'security':
      return (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-[var(--color-text)] mb-4">Change Password</h3>

            {message?.type === 'error' && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                {message.text}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Current Password</label>
                <div className="relative">
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm({...passwordForm, currentPassword: e.target.value})}
                    className="w-full px-4 py-2 bg-white border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords({...showPasswords, current: !showPasswords.current})}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                  >
                    {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">New Password</label>
                <div className="relative">
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                    className="w-full px-4 py-2 bg-white border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords({...showPasswords, new: !showPasswords.new})}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                  >
                    {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="mt-1 text-xs text-[var(--color-text-muted)]">At least 8 characters with letters and numbers</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Confirm Password</label>
                <div className="relative">
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                    className="w-full px-4 py-2 bg-white border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords({...showPasswords, confirm: !showPasswords.confirm})}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
                  >
                    {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <motion.button
                whileHover={{scale: 1.02}}
                whileTap={{scale: 0.98}}
                onClick={handleChangePassword}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Lock className="w-4 h-4" />
                {isSaving ? 'Changing...' : 'Change Password'}
              </motion.button>
            </div>
          </div>

          <div className="pt-6 border-t border-[var(--color-border)]">
            <h3 className="text-lg font-medium text-[var(--color-text)] mb-4">Sessions</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-[var(--color-surface)] rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <Globe className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-[var(--color-text)]">Current Session</p>
                    <p className="text-sm text-[var(--color-text-muted)]">Chrome on Windows</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Current</span>
              </div>
            </div>
          </div>
        </div>
      );

    case 'notifications':
      return (
        <div className="space-y-6">
          <h3 className="text-lg font-medium text-[var(--color-text)] mb-4">Notification Preferences</h3>

          <div className="space-y-4">
            {[
              {id: 'email', label: 'Email Notifications', description: 'Receive important updates', icon: Mail},
              {id: 'push', label: 'Push Notifications', description: 'Browser notifications', icon: Smartphone},
              {id: 'marketing', label: 'Marketing Emails', description: 'Product updates and offers', icon: Bell},
              {id: 'security', label: 'Security Alerts', description: 'Login and device alerts', icon: Shield}
            ].map((item) => {
              const Icon = item.icon;
              const isChecked = notifications[item.id as keyof typeof notifications];

              return (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 bg-white border border-[var(--color-border)] rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-[var(--color-text)]">{item.label}</p>
                      <p className="text-sm text-[var(--color-text-muted)]">{item.description}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => setNotifications({...notifications, [item.id]: !isChecked})}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      isChecked ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        isChecked ? 'translate-x-6' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      );

    case 'api':
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-[var(--color-text)]">API Keys</h3>
            <motion.button
              whileHover={{scale: 1.02}}
              whileTap={{scale: 0.98}}
              onClick={handleGenerateApiKey}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              <Key className="w-4 h-4" />
                Generate Key
            </motion.button>
          </div>

          <p className="text-sm text-[var(--color-text-muted)]">
              API keys for programmatic access. Keep them secure.
          </p>

          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="p-4 bg-white border border-[var(--color-border)] rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <input
                      type="text"
                      value={key.name}
                      onChange={(e) => {
                        setApiKeys(apiKeys.map(k =>
                          k.id === key.id ? {...k, name: e.target.value} : k
                        ));
                      }}
                      className="font-medium text-[var(--color-text)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1 -ml-1"
                    />
                    <div className="mt-2 flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
                      <span className="font-mono bg-[var(--color-surface)] px-2 py-1 rounded">{key.key.substring(0, 20)}...</span>
                      <span>Created: {key.createdAt}</span>
                      <span>Last used: {key.lastUsed}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteApiKey(key.id)}
                    className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  >
                      Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    default:
      return null;
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl">
        <h1 className="text-2xl font-bold text-[var(--color-text)] mb-6">Settings</h1>

        <div className="flex gap-6">
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {settingsSections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;

                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {section.label}
                    {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
                  </button>
                );
              })}
            </nav>
          </aside>

          <main className="flex-1 bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] p-6">
            {renderContent()}
          </main>
        </div>
      </div>
    </AppLayout>
  );
}
