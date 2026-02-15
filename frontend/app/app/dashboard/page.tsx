'use client';

import {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion} from 'framer-motion';
import {
  FileText,
  Plus,
  TrendingUp,
  Clock,
  ChevronRight,
  Upload,
  LayoutTemplate
} from 'lucide-react';
import {AppLayout} from '@/components/layout/AppLayout';
import {getUser, isAuthenticated} from '@/lib/api/auth';
import {
  getPresentations,
  createPresentation
} from '@/lib/api/presentations';
import {
  PresentationResponse,
  PresentationStatus
} from '@/types/presentation';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ElementType;
  color: string;
}

function StatCard({title, value, change, icon: Icon, color}: StatCardProps) {
  return (
    <motion.div
      whileHover={{y: -2}}
      className="bg-white rounded-xl p-6 shadow-[var(--shadow-card)] border border-[var(--color-border)]"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-[var(--color-text-muted)]">{title}</p>
          <p className="mt-2 text-3xl font-bold text-[var(--color-text)]">{value}</p>
          {change && (
            <p className="mt-1 text-sm text-green-600 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              {change}
            </p>
          )}
        </div>
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{backgroundColor: `${color}15`}}
        >
          <Icon className="w-6 h-6" style={{color}} />
        </div>
      </div>
    </motion.div>
  );
}

interface QuickActionProps {
  icon: React.ElementType;
  label: string;
  description: string;
  onClick: () => void;
  color: string;
}

function QuickAction({icon: Icon, label, description, onClick, color}: QuickActionProps) {
  return (
    <motion.button
      whileHover={{scale: 1.02}}
      whileTap={{scale: 0.98}}
      onClick={onClick}
      className="flex items-center gap-4 p-4 bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-card-hover)] transition-all text-left w-full"
    >
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{backgroundColor: `${color}15`}}
      >
        <Icon className="w-6 h-6" style={{color}} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-[var(--color-text)]">{label}</p>
        <p className="text-sm text-[var(--color-text-muted)]">{description}</p>
      </div>
      <ChevronRight className="w-5 h-5 text-[var(--color-text-placeholder)]" />
    </motion.button>
  );
}

function getStatusBadge(status: PresentationStatus) {
  const statusConfig = {
    draft: {label: 'Draft', color: 'bg-gray-100 text-gray-700'},
    generating: {label: 'Generating', color: 'bg-yellow-100 text-yellow-700'},
    completed: {label: 'Completed', color: 'bg-green-100 text-green-700'},
    published: {label: 'Published', color: 'bg-blue-100 text-blue-700'},
    archived: {label: 'Archived', color: 'bg-gray-100 text-gray-700'}
  };

  const config = statusConfig[status];
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [presentations, setPresentations] = useState<PresentationResponse[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    thisMonth: 0,
    recent: 0,
    storage: '0 MB'
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    try {
      const response = await getPresentations({page: 1, pageSize: 10});
      setPresentations(response.data.slice(0, 5));

      const total = response.meta.total;
      const thisMonth = response.data.filter(p => {
        const date = new Date(p.createdAt);
        const now = new Date();
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
      }).length;

      setStats({
        total,
        thisMonth,
        recent: response.data.filter(p => {
          const date = new Date(p.updatedAt);
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          return date > weekAgo;
        }).length,
        storage: `${(total * 2.5).toFixed(1)} MB`
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreatePPT = async () => {
    try {
      const response = await createPresentation({
        title: 'Untitled Presentation',
        description: ''
      });
      router.push(`/app/presentations/${response.id}/edit`);
    } catch (error) {
      console.error('Failed to create presentation:', error);
    }
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]">
            Welcome back, {getUser()?.name || 'User'}!
          </h1>
          <p className="mt-1 text-[var(--color-text-muted)]">
            Here is your dashboard overview
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total PPTs"
            value={stats.total}
            change="+12% vs last month"
            icon={FileText}
            color="#2563eb"
          />
          <StatCard
            title="This Month"
            value={stats.thisMonth}
            change="+5 vs last month"
            icon={TrendingUp}
            color="#10b981"
          />
          <StatCard
            title="Recent Edits"
            value={stats.recent}
            icon={Clock}
            color="#f59e0b"
          />
          <StatCard
            title="Storage Used"
            value={stats.storage}
            icon={Upload}
            color="#8b5cf6"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-semibold text-[var(--color-text)]">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <QuickAction
                icon={Plus}
                label="New PPT"
                description="Create presentation from scratch"
                onClick={handleCreatePPT}
                color="#2563eb"
              />
              <QuickAction
                icon={Upload}
                label="Import File"
                description="Import PPTX from local"
                onClick={() => {}}
                color="#10b981"
              />
              <QuickAction
                icon={LayoutTemplate}
                label="Use Template"
                description="Choose from template library"
                onClick={() => router.push('/app/presentations')}
                color="#f59e0b"
              />
              <QuickAction
                icon={FileText}
                label="From Outline"
                description="Generate PPT from outline"
                onClick={() => router.push('/app/outlines')}
                color="#8b5cf6"
              />
            </div>
          </div>

          {/* Recent Activity */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-[var(--color-text)]">Recent Edits</h2>
            <div className="bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] overflow-hidden">
              {presentations.length > 0 ? (
                <div className="divide-y divide-[var(--color-border)]">
                  {presentations.map((ppt) => (
                    <button
                      key={ppt.id}
                      onClick={() => router.push(`/app/presentations/${ppt.id}/edit`)}
                      className="w-full flex items-center gap-3 p-4 hover:bg-[var(--color-surface)] transition-colors text-left"
                    >
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-[var(--color-text)] truncate">
                          {ppt.title}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {getStatusBadge(ppt.status)}
                          <span className="text-xs text-[var(--color-text-muted)]">
                            {ppt.slideCount} slides
                          </span>
                        </div>
                      </div>
                      <span className="text-xs text-[var(--color-text-muted)]">
                        {new Date(ppt.updatedAt).toLocaleDateString()}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <FileText className="w-12 h-12 text-[var(--color-text-placeholder)] mx-auto mb-3" />
                  <p className="text-[var(--color-text-muted)]">No recent edits</p>
                </div>
              )}
              {presentations.length > 0 && (
                <button
                  onClick={() => router.push('/app/presentations')}
                  className="w-full py-3 text-sm text-blue-600 hover:bg-blue-50 transition-colors font-medium"
                >
                  View All
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
