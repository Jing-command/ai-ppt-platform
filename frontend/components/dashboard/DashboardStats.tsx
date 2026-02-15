'use client';

import { motion } from 'framer-motion';
import { AlertCircle, RefreshCw, FileText, TrendingUp, Target, Clock } from 'lucide-react';
import { DashboardStats as DashboardStatsType } from '@/lib/api/dashboard';
import { AnimatedNumber } from '@/components/ui/AnimatedNumber';
import { StatCardSkeleton } from '@/components/ui/StatCardSkeleton';

const statsConfig = [
  {
    label: '总大纲数',
    key: 'totalOutlines' as const,
    icon: FileText,
    gradient: 'from-blue-500 to-indigo-600',
    bgGradient: 'from-blue-50 to-indigo-50'
  },
  {
    label: '本周创建',
    key: 'createdThisWeek' as const,
    icon: TrendingUp,
    gradient: 'from-emerald-500 to-teal-600',
    bgGradient: 'from-emerald-50 to-teal-50'
  },
  {
    label: '已完成PPT',
    key: 'completedPpts' as const,
    icon: Target,
    gradient: 'from-purple-500 to-pink-600',
    bgGradient: 'from-purple-50 to-pink-50'
  },
  {
    label: '最近编辑',
    key: 'recentEdits' as const,
    icon: Clock,
    gradient: 'from-orange-500 to-amber-600',
    bgGradient: 'from-orange-50 to-amber-50'
  }
];

interface DashboardStatsProps {
  stats: DashboardStatsType | null;
  error: string | null;
  onRetry: () => void;
}

export function DashboardStats({ stats, error, onRetry }: DashboardStatsProps) {
  return (
    <motion.section className="mb-10">
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
          <button
            onClick={onRetry}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            重试
          </button>
        </motion.div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {!stats ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          statsConfig.map((stat, index) => {
            const Icon = stat.icon;
            const value = stats[stat.key];
            return (
              <motion.div
                key={stat.key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1, type: 'tween', duration: 0.1 }}
                whileHover={{ y: -4, scale: 1.02, transition: { duration: 0.1 } }}
                whileTap={{ scale: 0.98 }}
                className="group relative bg-white rounded-2xl p-5 sm:p-6 shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200 transition-all duration-100"
              >
                <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${stat.bgGradient} rounded-bl-full opacity-50 group-hover:opacity-80 transition-opacity duration-100`} />

                <div className="relative">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-100`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <p className="text-sm text-gray-500 mb-1">{stat.label}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                    <AnimatedNumber value={value} />
                  </p>
                </div>
              </motion.div>
            );
          })
        )}
      </div>
    </motion.section>
  );
}
