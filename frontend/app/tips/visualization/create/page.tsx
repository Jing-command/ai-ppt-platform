// app/tips/visualization/create/page.tsx
// 图表创建页面 - 数据源选择、字段映射和图表预览

'use client';

import {useState, useEffect, useCallback, Suspense} from 'react';
import {useRouter, useSearchParams} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
    ArrowLeft,
    CheckCircle,
    AlertCircle,
    FileSpreadsheet,
    Settings
} from 'lucide-react';
import type {
    ChartType,
    ParsedData,
    DataSource
} from '@/types/visualization';
import {ChartStorageManager} from '@/types/visualization';
import DataSourceSelector from '@/components/visualization/DataSourceSelector';
import ChartPreview from '@/components/visualization/ChartPreview';

/**
 * 图表创建页面内容组件
 * 使用 useSearchParams 需要包裹在 Suspense 中
 */
function CreatePageContent() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // 从 URL 参数获取图表类型
    const chartTypeParam = searchParams.get('type') as ChartType | null;
    // 从 URL 参数获取暂存图表 ID
    const storedIdParam = searchParams.get('storedId');

    // 当前图表类型
    const [chartType, setChartType] = useState<ChartType>(chartTypeParam || 'bar');
    // 解析后的数据
    const [parsedData, setParsedData] = useState<ParsedData | null>(null);
    // 暂存成功提示状态
    const [showStoreSuccess, setShowStoreSuccess] = useState(false);
    // 错误信息
    const [error, setError] = useState<string | null>(null);

    /**
     * 页面初始化
     * 处理 URL 参数
     */
    useEffect(() => {
    // 如果有图表类型参数，设置图表类型
        if (chartTypeParam) {
            setChartType(chartTypeParam);
        }

        // 如果有暂存图表 ID，加载暂存图表数据
        if (storedIdParam) {
            const storedChart = ChartStorageManager.getChartById(storedIdParam);
            if (storedChart) {
                setChartType(storedChart.type);
                // TODO: 根据数据源 ID 重新加载数据
                // 目前暂存图表不包含完整数据，需要用户重新上传
            }
        }
    }, [chartTypeParam, storedIdParam]);

    /**
     * 处理数据源选择
     * @param source - 选中的数据源
     */
    const handleDataSourceSelect = useCallback((source: DataSource) => {
        console.log('数据源已选择:', source);
    }, []);

    /**
     * 处理文件解析完成
     * @param data - 解析后的数据
     */
    const handleFileParsed = useCallback((data: ParsedData) => {
        setParsedData(data);
        setError(null);
    }, []);

    /**
     * 处理图表暂存成功
     */
    const handleStoreSuccess = useCallback(() => {
    // 显示成功提示
        setShowStoreSuccess(true);

        // 3 秒后自动隐藏提示
        setTimeout(() => {
            setShowStoreSuccess(false);
        }, 3000);
    }, []);

    /**
     * 处理返回按钮点击
     */
    const handleBack = () => {
        router.push('/tips/visualization');
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
                            onClick={handleBack}
                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors group"
                        >
                            <div className="p-2 rounded-lg group-hover:bg-gray-100 transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                            </div>
                            <span className="font-medium">返回</span>
                        </button>

                        {/* 标题 */}
                        <div className="ml-6 flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/20">
                                <Settings className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="font-semibold text-gray-900">创建图表</h1>
                                <p className="text-xs text-gray-500">
                                    当前类型：{chartType}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.nav>

            {/* 暂存成功提示 */}
            <AnimatePresence>
                {showStoreSuccess && (
                    <motion.div
                        initial={{opacity: 0, y: -20}}
                        animate={{opacity: 1, y: 0}}
                        exit={{opacity: 0, y: -20}}
                        transition={{duration: 0.1}}
                        className="fixed top-20 left-1/2 -translate-x-1/2 z-50"
                    >
                        <div className="flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-200 rounded-lg shadow-lg">
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            <span className="text-sm font-medium text-green-700">
                                图表已暂存成功
                            </span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* 主内容区域 */}
            <main className="relative z-10 h-[calc(100vh-64px)] flex">
                {/* 左侧：数据源选择 */}
                <motion.div
                    initial={{opacity: 0, x: -20}}
                    animate={{opacity: 1, x: 0}}
                    transition={{duration: 0.1, delay: 0.1}}
                    className="w-1/3 min-w-[320px] max-w-[400px] border-r border-gray-200/50 bg-white/50 backdrop-blur-sm overflow-y-auto"
                >
                    <div className="p-6">
                        {/* 区域标题 */}
                        <div className="mb-6">
                            <div className="flex items-center gap-2 mb-2">
                                <FileSpreadsheet className="w-5 h-5 text-blue-500" />
                                <h2 className="text-lg font-semibold text-gray-900">
                                    数据源
                                </h2>
                            </div>
                            <p className="text-sm text-gray-500">
                                上传文件或连接数据库获取数据
                            </p>
                        </div>

                        {/* 数据源选择器 */}
                        <DataSourceSelector
                            onSelect={handleDataSourceSelect}
                            onFileParsed={handleFileParsed}
                        />

                        {/* 错误提示 */}
                        {error && (
                            <motion.div
                                initial={{opacity: 0, y: 10}}
                                animate={{opacity: 1, y: 0}}
                                className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg"
                            >
                                <div className="flex items-start gap-2">
                                    <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />
                                    <div>
                                        <p className="text-sm font-medium text-red-700">
                                            数据解析失败
                                        </p>
                                        <p className="text-xs text-red-600 mt-1">
                                            {error}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </div>
                </motion.div>

                {/* 右侧：图表预览 */}
                <motion.div
                    initial={{opacity: 0, x: 20}}
                    animate={{opacity: 1, x: 0}}
                    transition={{duration: 0.1, delay: 0.2}}
                    className="flex-1 bg-gray-50/50"
                >
                    {parsedData ? (
                    // 有数据时显示图表预览
                        <ChartPreview
                            chartType={chartType}
                            data={parsedData}
                            onStore={handleStoreSuccess}
                        />
                    ) : (
                    // 无数据时显示提示
                        <div className="h-full flex flex-col items-center justify-center text-gray-400">
                            <FileSpreadsheet className="w-20 h-20 mb-4" />
                            <p className="text-lg font-medium text-gray-500 mb-2">
                                请先上传数据文件
                            </p>
                            <p className="text-sm text-gray-400">
                                支持 Excel、CSV、JSON 格式
                            </p>
                        </div>
                    )}
                </motion.div>
            </main>
        </div>
    );
}

/**
 * 图表创建页面组件
 * 包含 Suspense 边界以支持 useSearchParams
 */
export default function CreatePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
                <div className="text-gray-400">加载中...</div>
            </div>
        }>
            <CreatePageContent />
        </Suspense>
    );
}
