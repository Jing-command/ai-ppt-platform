import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getUser, isAuthenticated, clearAuthData } from '@/lib/api/auth';
import { getDashboardStats, DashboardStats } from '@/lib/api/dashboard';
import { User } from '@/types/auth';

export function useDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
      console.error('获取 Dashboard 数据失败:', err);
    }
  }, []);

  const handleRetry = useCallback(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleLogout = useCallback(() => {
    clearAuthData();
    router.push('/login');
  }, [router]);

  const handleUserUpdate = useCallback((updatedUser: User) => {
    setUser(updatedUser);
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const currentUser = getUser();
    setUser(currentUser);
    setIsLoading(false);

    fetchDashboardData();
  }, [router, fetchDashboardData]);

  return {
    user,
    isLoading,
    stats,
    error,
    handleRetry,
    handleLogout,
    handleUserUpdate
  };
}
