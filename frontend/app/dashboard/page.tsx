'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { UserProfileModal } from '@/components/layout/UserProfileModal';
import { useDashboard } from '@/hooks/useDashboard';
import { containerVariants } from '@/constants/animations';
import {
  DashboardNavbar,
  DashboardHero,
  DashboardStats,
  DashboardQuickActions,
  DashboardRecentActivity,
  DashboardFeatures,
  DashboardTemplates,
  DashboardTips,
  DashboardFooter,
  DashboardBackground,
  DashboardLoading
} from '@/components/dashboard';

export default function DashboardPage() {
  const { user, isLoading, stats, error, handleRetry, handleLogout, handleUserUpdate } = useDashboard();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  if (isLoading) {
    return <DashboardLoading />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      <DashboardBackground />
      
      <DashboardNavbar
        user={user}
        onLogout={handleLogout}
        onProfileClick={() => setIsProfileModalOpen(true)}
      />

      <main className="relative z-10 max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <DashboardHero user={user} />
          <DashboardStats stats={stats} error={error} onRetry={handleRetry} />
          <DashboardQuickActions />
          <DashboardFeatures />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
            <DashboardRecentActivity stats={stats} />
            <DashboardTemplates />
          </div>

          <DashboardTips />
          <DashboardFooter />
        </motion.div>
      </main>

      {user && (
        <UserProfileModal
          user={user}
          isOpen={isProfileModalOpen}
          onClose={() => setIsProfileModalOpen(false)}
          onUserUpdate={handleUserUpdate}
        />
      )}
    </div>
  );
}
