/**
 * Dashboard API 客户端
 * 提供 Dashboard 页面数据获取功能
 */

import {apiClient} from './client';

// Dashboard 统计数据类型
export interface RecentActivity {
  id: string;
  title: string;
  type: 'outline' | 'ppt';
  status: 'completed' | 'draft' | 'published' | 'generating' | 'archived';
  updatedAt: string;
}

export interface DashboardStats {
  totalOutlines: number;
  createdThisWeek: number;
  completedPpts: number;
  recentEdits: number;
  recentActivities: RecentActivity[];
}

// API 错误类型
export interface DashboardApiError {
  code: string;
  message: string;
}

/**
 * 获取 Dashboard 统计数据
 * @returns DashboardStats Dashboard 统计数据
 * @throws Error 当请求失败时抛出错误
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    return response.data;
  } catch (error) {
    // 处理 API 错误
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: DashboardApiError } };
      const errorData = axiosError.response?.data;
      if (errorData) {
        throw new Error(errorData.message || '获取数据失败');
      }
    }
    throw new Error('网络错误，请检查网络连接');
  }
}

export default {
  getDashboardStats
};
