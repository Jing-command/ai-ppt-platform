'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { getUser, clearAuthData, isAuthenticated } from '@/lib/api/auth';
import { User } from '@/types/auth';
import {
  FileText,
  Layers,
  Plus,
  LogOut,
  ChevronRight,
  Sparkles,
  TrendingUp,
  Target,
  Clock,
  Zap,
  Lightbulb,
  ArrowRight,
  BarChart3,
  Palette,
  Plug,
  MoreHorizontal,
} from 'lucide-react';

// 动画变体配置
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  },
};

// 数字动画组件
function AnimatedNumber({ value, duration = 2 }: { value: number; duration?: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
      // 使用 ease-out 缓动函数
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.floor(easeOut * value));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);

  return <span>{displayValue}</span>;
}

// 获取个性化问候语
function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return '早上好';
  if (hour < 18) return '下午好';
  return '晚上好';
}

// 获取用户头像首字母
function getInitials(name: string | undefined): string {
  if (!name) return 'U';
  return name.charAt(0).toUpperCase();
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 模拟统计数据（后续可对接真实 API）
  const stats = [
    {
      label: '总大纲数',
      value: 24,
      icon: FileText,
      gradient: 'from-blue-500 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50',
    },
    {
      label: '本周创建',
      value: 5,
      icon: TrendingUp,
      gradient: 'from-emerald-500 to-teal-600',
      bgGradient: 'from-emerald-50 to-teal-50',
    },
    {
      label: '已完成PPT',
      value: 12,
      icon: Target,
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50',
    },
    {
      label: '最近编辑',
      value: 3,
      icon: Clock,
      gradient: 'from-orange-500 to-amber-600',
      bgGradient: 'from-orange-50 to-amber-50',
    },
  ];

  // 快捷操作配置
  const quickActions = [
    {
      title: 'AI 生成大纲',
      description: '智能生成演示文稿结构',
      icon: Sparkles,
      href: '/outlines/new',
      gradient: 'from-blue-500 via-indigo-500 to-purple-600',
      featured: true,
    },
    {
      title: '查看我的大纲',
      description: '管理和编辑现有大纲',
      icon: FileText,
      href: '/outlines',
      gradient: 'from-emerald-500 to-teal-600',
      featured: false,
    },
    {
      title: '我的 PPT',
      description: '查看和编辑演示文稿',
      icon: Palette,
      href: '/presentations',
      gradient: 'from-purple-500 to-pink-600',
      featured: false,
    },
    {
      title: '数据连接器',
      description: '管理数据库和 API 连接',
      icon: Plug,
      href: '/connectors',
      gradient: 'from-orange-500 to-amber-600',
      featured: false,
    },
  ];

  // 最近活动模拟数据
  const recentActivities = [
    {
      id: 1,
      title: 'Q4 季度工作总结',
      type: 'outline',
      status: 'completed',
      updatedAt: '2小时前',
    },
    {
      id: 2,
      title: '产品发布会策划',
      type: 'ppt',
      status: 'draft',
      updatedAt: '昨天',
    },
    {
      id: 3,
      title: '团队年度培训计划',
      type: 'outline',
      status: 'completed',
      updatedAt: '3天前',
    },
  ];

  // 使用技巧
  const tips = [
    {
      icon: Lightbulb,
      title: '提示词技巧',
      desc: '如何写出更有效的 AI 提示词',
      color: 'text-amber-500',
      bgColor: 'bg-amber-50',
    },
    {
      icon: BarChart3,
      title: '数据可视化',
      desc: '让图表更有说服力的方法',
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      icon: Zap,
      title: '快捷操作',
      desc: '提升制作效率的快捷键',
      color: 'text-purple-500',
      bgColor: 'bg-purple-50',
    },
  ];

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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-gray-500 font-medium">加载中...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -left-40 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-pink-200/20 rounded-full blur-3xl" />
      </div>

      {/* 导航栏 */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-xl bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                AI PPT
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 hidden sm:block">
                {user?.email}
              </span>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 
                         hover:text-red-700 hover:bg-red-50 rounded-xl transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">退出</span>
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* 主内容区域 */}
      <main className="relative z-10 max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Section - 欢迎区域 */}
          <motion.section variants={itemVariants} className="mb-10">
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 p-8 sm:p-12 shadow-2xl shadow-blue-500/25">
              {/* 装饰背景 */}
              <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-500/30 rounded-full blur-3xl" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl" />
              </div>

              <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                <div className="flex-1">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 backdrop-blur-sm rounded-full mb-4"
                  >
                    <Zap className="w-4 h-4 text-yellow-300" />
                    <span className="text-sm font-medium text-white/90">
                      {getGreeting()}，开启高效创作
                    </span>
                  </motion.div>
                  <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3"
                  >
                    欢迎回来，{user?.name || '用户'}！
                  </motion.h1>
                  <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="text-lg text-white/80 max-w-xl"
                  >
                    今天想要创建什么样的演示文稿？让 AI 助你轻松完成专业设计。
                  </motion.p>
                </div>

                {/* 用户头像 */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5, type: 'spring' }}
                  className="flex-shrink-0"
                >
                  <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white/20 backdrop-blur-sm border-2 border-white/30 flex items-center justify-center shadow-xl">
                    <span className="text-3xl sm:text-4xl font-bold text-white">
                      {getInitials(user?.name)}
                    </span>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.section>

          {/* 统计卡片区域 */}
          <motion.section variants={itemVariants} className="mb-10">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    className="group relative bg-white rounded-2xl p-5 sm:p-6 shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200 transition-all duration-300"
                  >
                    {/* 渐变背景装饰 */}
                    <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${stat.bgGradient} rounded-bl-full opacity-50 group-hover:opacity-80 transition-opacity`} />
                    
                    <div className="relative">
                      <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <p className="text-sm text-gray-500 mb-1">{stat.label}</p>
                      <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                        <AnimatedNumber value={stat.value} />
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.section>

          {/* 快捷操作区域 */}
          <motion.section variants={itemVariants} className="mb-10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">快速开始</h2>
              <Link
                href="/outlines"
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors"
              >
                查看全部
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <motion.div
                    key={action.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    whileHover={{ y: -6, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Link
                      href={action.href}
                      className={`group block relative overflow-hidden rounded-2xl p-6 h-full transition-all duration-300 ${
                        action.featured
                          ? 'bg-gradient-to-br ' + action.gradient + ' shadow-xl shadow-blue-500/25 hover:shadow-2xl hover:shadow-blue-500/30'
                          : 'bg-white shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200'
                      }`}
                    >
                      {/* 背景装饰 */}
                      {!action.featured && (
                        <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${action.gradient} opacity-5 rounded-bl-full group-hover:opacity-10 transition-opacity`} />
                      )}
                      {action.featured && (
                        <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/20 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
                      )}

                      <div className="relative">
                        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3 ${
                          action.featured
                            ? 'bg-white/20 backdrop-blur-sm'
                            : `bg-gradient-to-br ${action.gradient} shadow-lg`
                        }`}>
                          <Icon className={`w-7 h-7 ${action.featured ? 'text-white' : 'text-white'}`} />
                        </div>
                        <h3 className={`text-lg font-semibold mb-2 ${action.featured ? 'text-white' : 'text-gray-900 group-hover:text-blue-600 transition-colors'}`}>
                          {action.title}
                        </h3>
                        <p className={`text-sm ${action.featured ? 'text-white/80' : 'text-gray-500'}`}>
                          {action.description}
                        </p>

                        {/* 箭头指示 */}
                        <div className={`mt-4 flex items-center gap-1 text-sm font-medium ${
                          action.featured ? 'text-white' : 'text-gray-400 group-hover:text-blue-600'
                        } transition-colors`}>
                          <span>开始</span>
                          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
            </div>
          </motion.section>

          {/* 最近活动 + 使用技巧 */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* 最近编辑 */}
            <motion.section variants={itemVariants} className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 border border-gray-100 overflow-hidden">
                <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
                      <Clock className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">最近编辑</h3>
                      <p className="text-sm text-gray-500">您最近处理的内容</p>
                    </div>
                  </div>
                  <Link
                    href="/outlines"
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <MoreHorizontal className="w-5 h-5" />
                  </Link>
                </div>

                <div className="p-2">
                  {recentActivities.length > 0 ? (
                    <div className="divide-y divide-gray-50">
                      {recentActivities.map((activity, index) => (
                        <motion.div
                          key={activity.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.5 + index * 0.1 }}
                          className="group flex items-center justify-between p-4 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                              activity.type === 'outline'
                                ? 'bg-blue-50 text-blue-600'
                                : 'bg-purple-50 text-purple-600'
                            }`}>
                              {activity.type === 'outline' ? (
                                <FileText className="w-5 h-5" />
                              ) : (
                                <Layers className="w-5 h-5" />
                              )}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                                {activity.title}
                              </h4>
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-xs text-gray-500">{activity.updatedAt}</span>
                                <span className="w-1 h-1 rounded-full bg-gray-300" />
                                <span className={`text-xs ${
                                  activity.status === 'completed'
                                    ? 'text-green-600'
                                    : 'text-amber-600'
                                }`}>
                                  {activity.status === 'completed' ? '已完成' : '草稿'}
                                </span>
                              </div>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    // 空状态
                    <div className="py-12 text-center">
                      <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-50 rounded-full mb-4">
                        <FileText className="w-8 h-8 text-gray-300" />
                      </div>
                      <h4 className="text-lg font-medium text-gray-900 mb-2">
                        还没有大纲
                      </h4>
                      <p className="text-gray-500 mb-4 max-w-sm mx-auto">
                        创建你的第一个 AI 生成大纲，开启智能演示之旅
                      </p>
                      <Link
                        href="/outlines/new"
                        className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/25"
                      >
                        <Plus className="w-4 h-4" />
                        立即创建
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </motion.section>

            {/* 使用技巧 */}
            <motion.section variants={itemVariants}>
              <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 border border-gray-100 overflow-hidden h-full">
                <div className="px-6 py-5 border-b border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-100 to-orange-100 flex items-center justify-center">
                      <Lightbulb className="w-5 h-5 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">使用技巧</h3>
                      <p className="text-sm text-gray-500">提升创作效率</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 space-y-2">
                  {tips.map((tip, index) => {
                    const Icon = tip.icon;
                    return (
                      <motion.div
                        key={tip.title}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + index * 0.1 }}
                        whileHover={{ x: 4 }}
                        className="group flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
                      >
                        <div className={`w-10 h-10 rounded-lg ${tip.bgColor} flex items-center justify-center flex-shrink-0`}>
                          <Icon className={`w-5 h-5 ${tip.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                            {tip.title}
                          </h4>
                          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                            {tip.desc}
                          </p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-blue-600 mt-1 transition-colors" />
                      </motion.div>
                    );
                  })}
                </div>

                {/* 底部 CTA */}
                <div className="p-4 border-t border-gray-100">
                  <Link
                    href="/help"
                    className="flex items-center justify-center gap-2 w-full py-3 text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-colors"
                  >
                    <span>查看帮助中心</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </motion.section>
          </div>

          {/* 底部功能推荐 - 热门模板 */}
          <motion.section variants={itemVariants} className="mt-10">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">热门模板</h2>
                <p className="text-sm text-gray-500 mt-1">快速开始您的下一个项目</p>
              </div>
              <Link
                href="/templates"
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors"
              >
                浏览全部
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              {[
                { title: '工作周报', icon: FileText, color: 'from-blue-500 to-indigo-600', desc: '简洁专业的周报结构' },
                { title: '商业计划', icon: BarChart3, color: 'from-purple-500 to-pink-600', desc: '完整商业计划框架' },
                { title: '教育课件', icon: Layers, color: 'from-emerald-500 to-teal-600', desc: '互动式教学设计' },
                { title: '营销方案', icon: Target, color: 'from-orange-500 to-amber-600', desc: '营销活动策划模板' },
              ].map((template, index) => {
                const Icon = template.icon;
                return (
                  <motion.div
                    key={template.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    className="group cursor-pointer"
                  >
                    <div className="relative bg-white rounded-2xl p-5 shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200 transition-all duration-300 overflow-hidden">
                      <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${template.color} opacity-5 rounded-bl-full group-hover:opacity-10 transition-opacity`} />
                      
                      <div className="relative">
                        <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${template.color} shadow-lg mb-4 group-hover:scale-110 transition-transform duration-300`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {template.title}
                        </h3>
                        <p className="text-sm text-gray-500">{template.desc}</p>
                        
                        <div className="mt-4 flex items-center gap-2 text-sm text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Sparkles className="w-4 h-4" />
                          <span>使用此模板</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
}
