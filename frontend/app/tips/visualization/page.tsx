// app/tips/visualization/page.tsx
// 数据可视化主页 - 图表选择和暂存管理

'use client';

import {useState, useCallback} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import dynamic from 'next/dynamic';
import {
    ArrowLeft,
    Sparkles,
    ChevronDown,
    FolderOpen
} from 'lucide-react';
import type {ChartType, StoredChart} from '@/types/visualization';

// 动态导入大型组件，优化首屏加载
const ChartSelector = dynamic(
    () => import('@/components/visualization/ChartSelector'),
    {
        loading: () => (
            <div className="flex items-center justify-center py-20">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
        ),
        ssr: false
    }
);

const StoredCharts = dynamic(
    () => import('@/components/visualization/StoredCharts'),
    {
        loading: () => (
            <div className="flex items-center justify-center py-10 text-gray-400">
                加载中...
            </div>
        ),
        ssr: false
    }
);

/**
 * 数据可视化主页组件
 * 提供图表选择、AI 辅助入口和暂存图表管理功能
 */
export default function VisualizationPage() {
    const router = useRouter();

    // 暂存图表面板展开状态
    const [isStoredPanelOpen, setIsStoredPanelOpen] = useState(false);

    /**
     * 处理图表选择
     * @param chartType - 选中的图表类型
     */
    const handleChartSelect = useCallback((chartType: ChartType) => {
    // 跳转到图表创建页，传递图表类型参数
        router.push(`/tips/visualization/create?type=${chartType}`);
    }, [router]);

    /**
     * 处理 AI 辅助选图入口点击
     */
    const handleAIAssistClick = useCallback(() => {
    // 跳转到 AI 辅助页
        router.push('/tips/visualization/ai-assist');
    }, [router]);

    /**
     * 处理暂存图表选择
     * @param chart - 选中的暂存图表
     */
    const handleStoredChartSelect = useCallback((chart: StoredChart) => {
    // 跳转到图表创建页，传递图表 ID 参数
        router.push(`/tips/visualization/create?storedId=${chart.id}`);
    }, [router]);

    /**
     * 切换暂存面板展开状态
     */
    const toggleStoredPanel = () => {
        setIsStoredPanelOpen(prev => !prev);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
            {/* 背景装饰 */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
            </div>

            {/* 导航栏 */}
            <motion.nav
                initial={{opacity: 0, y: -20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.1}}
                className="relative z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center">
                        {/* 返回按钮 */}
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors group"
                        >
                            <div className="p-2 rounded-lg group-hover:bg-gray-100 transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                            </div>
                            <span className="font-medium">返回</span>
                        </button>

                        {/* 标题 */}
                        <div className="ml-6 flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <FolderOpen className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="font-semibold text-gray-900">数据可视化</h1>
                                <p className="text-xs text-gray-500">选择图表类型，创建精美图表</p>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.nav>

            {/* 主内容区域 */}
            <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {/* AI 辅助选图入口 */}
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    transition={{duration: 0.1, delay: 0.1}}
                    className="mb-6"
                >
                    <motion.button
                        onClick={handleAIAssistClick}
                        // 按钮动画：悬停上浮和发光效果
                        whileHover={{y: -2, scale: 1.01}}
                        whileTap={{scale: 0.99}}
                        transition={{duration: 0.1}}
                        className="
                            w-full p-5 rounded-xl
                            bg-gradient-to-r from-purple-500 via-indigo-500 to-blue-500
                            text-white shadow-lg shadow-purple-500/25
                            flex items-center justify-center gap-3
                            hover:shadow-xl hover:shadow-purple-500/30
                            transition-shadow duration-100
                        "
                    >
                        {/* AI 图标 */}
                        <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                            <Sparkles className="w-6 h-6" />
                        </div>

                        {/* 文字说明 */}
                        <div className="text-left">
                            <h2 className="text-lg font-semibold">AI 智能选图</h2>
                            <p className="text-sm text-white/80">
                                上传数据，让 AI 为你推荐最合适的图表类型
                            </p>
                        </div>
                    </motion.button>
                </motion.div>

                {/* 图表选择区域 */}
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    transition={{duration: 0.1, delay: 0.2}}
                    className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm p-6"
                >
                    <ChartSelector onSelect={handleChartSelect} />
                </motion.div>

                {/* 暂存图表面板 */}
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    transition={{duration: 0.1, delay: 0.3}}
                    className="mt-6 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm overflow-hidden"
                >
                    {/* 面板头部（可点击折叠） */}
                    <button
                        onClick={toggleStoredPanel}
                        className="
                            w-full flex items-center justify-between
                            px-4 py-3 bg-gray-50/50
                            hover:bg-gray-100/50 transition-colors
                        "
                    >
                        <div className="flex items-center gap-2">
                            <FolderOpen className="w-5 h-5 text-orange-500" />
                            <span className="font-medium text-gray-800">暂存图表</span>
                            <span className="text-xs text-gray-500">点击展开查看</span>
                        </div>

                        {/* 展开/收起图标 */}
                        <motion.div
                            animate={{rotate: isStoredPanelOpen ? 180 : 0}}
                            transition={{duration: 0.1}}
                        >
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                        </motion.div>
                    </button>

                    {/* 面板内容 */}
                    <AnimatePresence>
                        {isStoredPanelOpen && (
                            <motion.div
                                initial={{height: 0, opacity: 0}}
                                animate={{height: 'auto', opacity: 1}}
                                exit={{height: 0, opacity: 0}}
                                transition={{duration: 0.1}}
                                className="overflow-hidden"
                            >
                                <div className="h-80 border-t border-gray-200/50">
                                    <StoredCharts onSelect={handleStoredChartSelect} />
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </main>
        </div>
    );
}
