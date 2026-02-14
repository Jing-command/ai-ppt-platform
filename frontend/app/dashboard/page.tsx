'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUser, clearAuthData, isAuthenticated } from '@/lib/api/auth';
import { User } from '@/types/auth';
import { 
  FileText, 
  Layers, 
  Database, 
  Plus, 
  LogOut,
  ChevronRight
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const currentUser = getUser();
    setUser(currentUser);
    setIsLoading(false);
  }, [router]);

  const handleLogout = () => {
    clearAuthData();
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  const quickActions = [
    {
      title: '创建大纲',
      description: '使用 AI 生成演示文稿大纲',
      icon: Layers,
      href: '/outlines/new',
      color: 'bg-blue-500',
    },
    {
      title: '我的大纲',
      description: '管理和编辑现有大纲',
      icon: FileText,
      href: '/outlines',
      color: 'bg-green-500',
    },
    {
      title: '我的 PPT',
      description: '查看和编辑演示文稿',
      icon: Layers,
      href: '/presentations',
      color: 'bg-purple-500',
    },
    {
      title: '数据连接器',
      description: '管理数据库和 API 连接',
      icon: Database,
      href: '/connectors',
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">AI PPT 平台</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user?.name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm font-medium text-red-600 
                           hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
              >
                <LogOut className="w-4 h-4 mr-1" />
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区域 */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* 欢迎区域 */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            欢迎回来，{user?.name || '用户'}！
          </h2>
          <p className="mt-1 text-gray-600">
            开始创建你的智能演示文稿
          </p>
        </div>

        {/* 快捷操作卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {quickActions.map((action) => (
            <Link
              key={action.title}
              href={action.href}
              className="group block bg-white rounded-lg shadow-sm border border-gray-200 
                         hover:shadow-md hover:border-gray-300 transition-all duration-200"
            >
              <div className="p-6">
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${action.color} mb-4`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  {action.title}
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {action.description}
                </p>
                <div className="mt-4 flex items-center text-sm text-blue-600">
                  <span>进入</span>
                  <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 最近活动 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">快速开始</h3>
                <Link 
                  href="/outlines/new" 
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium 
                             rounded-md hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  新建大纲
                </Link>
              </div>
              <div className="p-6">
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                    <FileText className="w-8 h-8 text-gray-400" />
                  </div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    还没有大纲
                  </h4>
                  <p className="text-gray-600 mb-4">
                    创建你的第一个 AI 生成大纲，开启智能演示之旅
                  </p>
                  <Link 
                    href="/outlines/new"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium 
                               rounded-md hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    立即创建
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* 用户信息侧边栏 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">账户信息</h3>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">用户名</label>
                  <p className="mt-1 text-gray-900">{user?.name || '-'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">邮箱</label>
                  <p className="mt-1 text-gray-900">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">注册时间</label>
                  <p className="mt-1 text-gray-900">
                    {user?.createdAt 
                      ? new Date(user.createdAt).toLocaleDateString('zh-CN')
                      : '-'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
