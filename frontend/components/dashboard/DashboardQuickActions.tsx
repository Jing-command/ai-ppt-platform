'use client';

import Link from 'next/link';
import {motion} from 'framer-motion';
import {ArrowRight, ChevronRight, Sparkles, FileText, Palette, Plug} from 'lucide-react';

const quickActions = [
    {
        title: 'AI 生成大纲',
        description: '智能生成演示文稿结构',
        icon: Sparkles,
        href: '/outlines/new',
        gradient: 'from-blue-500 via-indigo-500 to-purple-600',
        featured: true
    },
    {
        title: '查看我的大纲',
        description: '管理和编辑现有大纲',
        icon: FileText,
        href: '/outlines',
        gradient: 'from-emerald-500 to-teal-600',
        featured: false
    },
    {
        title: '我的 PPT',
        description: '查看和编辑演示文稿',
        icon: Palette,
        href: '/presentations',
        gradient: 'from-purple-500 to-pink-600',
        featured: false
    },
    {
        title: '数据连接器',
        description: '管理数据库和 API 连接',
        icon: Plug,
        href: '/connectors',
        gradient: 'from-orange-500 to-amber-600',
        featured: false
    }
];

export function DashboardQuickActions() {
    return (
        <motion.section className="mb-10">
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
                            initial={{opacity: 0, y: 20}}
                            animate={{opacity: 1, y: 0}}
                            transition={{delay: 0.4 + index * 0.1, type: 'tween', duration: 0.1}}
                            whileHover={{y: -6, scale: 1.02, transition: {duration: 0.1}}}
                            whileTap={{scale: 0.98}}
                        >
                            <Link
                                href={action.href}
                                className={`group block relative overflow-hidden rounded-2xl p-6 h-full transition-all duration-100 ${
                                    action.featured
                                        ? 'bg-gradient-to-br ' + action.gradient + ' shadow-xl shadow-blue-500/25 hover:shadow-2xl hover:shadow-blue-500/30'
                                        : 'bg-white shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200'
                                }`}
                            >
                                {!action.featured && (
                                    <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${action.gradient} opacity-5 rounded-bl-full group-hover:opacity-10 transition-opacity duration-100`} />
                                )}
                                {action.featured && (
                                    <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/20 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-100" />
                                )}

                                <div className="relative">
                                    <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 transition-transform duration-100 group-hover:scale-110 group-hover:rotate-3 ${
                                        action.featured
                                            ? 'bg-white/20 backdrop-blur-sm'
                                            : `bg-gradient-to-br ${action.gradient} shadow-lg`
                                    }`}>
                                        <Icon className="w-7 h-7 text-white" />
                                    </div>
                                    <h3 className={`text-lg font-semibold mb-2 ${action.featured ? 'text-white' : 'text-gray-900 group-hover:text-blue-600 transition-colors duration-100'}`}>
                                        {action.title}
                                    </h3>
                                    <p className={`text-sm ${action.featured ? 'text-white/80' : 'text-gray-500'}`}>
                                        {action.description}
                                    </p>

                                    <div className={`mt-4 flex items-center gap-1 text-sm font-medium ${
                                        action.featured ? 'text-white' : 'text-gray-400 group-hover:text-blue-600'
                                    } transition-colors duration-100`}>
                                        <span>开始</span>
                                        <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-100" />
                                    </div>
                                </div>
                            </Link>
                        </motion.div>
                    );
                })}
            </div>
        </motion.section>
    );
}
