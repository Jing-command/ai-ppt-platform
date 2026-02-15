'use client';

import Link from 'next/link';
import {motion} from 'framer-motion';
import {Clock, MoreHorizontal, Plus, FileText} from 'lucide-react';
import {DashboardStats} from '@/lib/api/dashboard';
import {ActivityItem} from './ActivityItem';

interface DashboardRecentActivityProps {
  stats: DashboardStats | null;
}

export function DashboardRecentActivity({stats}: DashboardRecentActivityProps) {
    return (
        <motion.section className="lg:col-span-2">
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
                    {!stats ? (
                        <div className="space-y-2 p-2">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="flex items-center gap-4 p-4 animate-pulse">
                                    <div className="w-10 h-10 rounded-xl bg-gray-200" />
                                    <div className="flex-1">
                                        <div className="h-4 w-32 bg-gray-200 rounded mb-2" />
                                        <div className="h-3 w-20 bg-gray-200 rounded" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : stats.recentActivities.length > 0 ? (
                        <div className="divide-y divide-gray-50">
                            {stats.recentActivities.map((activity, index) => (
                                <ActivityItem key={activity.id} activity={activity} index={index} />
                            ))}
                        </div>
                    ) : (
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
    );
}
