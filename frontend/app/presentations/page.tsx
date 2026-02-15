'use client';

import {useEffect, useState, useCallback} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {Plus, FileText, Loader2, AlertCircle, RefreshCw, Clock, Layers, Presentation} from 'lucide-react';
import {PresentationResponse, PresentationStatus} from '@/types/presentation';
import {getPresentations, deletePresentation} from '@/lib/api/presentations';
import {AxiosError} from 'axios';

const containerVariants = {
    hidden: {opacity: 0},
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.08,
            delayChildren: 0.1
        }
    }
};

const itemVariants = {
    hidden: {opacity: 0, y: 20},
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.4,
            ease: [0.4, 0, 0.2, 1] as const
        }
    }
};

const statusMap: Record<PresentationStatus, { label: string; color: string }> = {
    draft: {label: '草稿', color: 'bg-gray-100 text-gray-700'},
    generating: {label: '生成中', color: 'bg-blue-100 text-blue-700'},
    completed: {label: '已完成', color: 'bg-green-100 text-green-700'},
    published: {label: '已发布', color: 'bg-purple-100 text-purple-700'},
    archived: {label: '已归档', color: 'bg-red-100 text-red-700'}
};

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

export default function PresentationsPage() {
    const router = useRouter();
    const [presentations, setPresentations] = useState<PresentationResponse[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [deleteLoading, setDeleteLoading] = useState<string | null>(null);

    const fetchPresentations = useCallback(async () => {
        setIsLoading(true);
        setError('');

        try {
            const response = await getPresentations({page: 1, pageSize: 100});
            setPresentations(response.data);
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                setError('请先登录');
                router.push('/login');
            } else {
                setError('获取 PPT 列表失败，请稍后重试');
            }
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    useEffect(() => {
        fetchPresentations();
    }, [fetchPresentations]);

    const handleEdit = (presentation: PresentationResponse) => {
        router.push(`/presentations/${presentation.id}`);
    };

    const handleDelete = async (presentation: PresentationResponse) => {
        if (!confirm(`确定要删除 PPT "${presentation.title}" 吗？此操作不可恢复。`)) {
            return;
        }

        setDeleteLoading(presentation.id);

        try {
            await deletePresentation(presentation.id);
            setPresentations((prev) => prev.filter((p) => p.id !== presentation.id));
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                router.push('/login');
            } else {
                alert('删除失败：' + ((axiosError.response?.data as { message?: string })?.message || '请稍后重试'));
            }
        } finally {
            setDeleteLoading(null);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--color-background)]">
            {/* 导航栏 */}
            <nav className="bg-white shadow-sm border-b border-[var(--color-border)]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-4">
                            <a
                                href="/dashboard"
                                className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                            >
                仪表盘
                            </a>
                            <span className="text-[var(--color-border)]">/</span>
                            <h1 className="text-lg font-semibold text-[var(--color-text)]">PPT 管理</h1>
                        </div>

                        <motion.button
                            onClick={() => router.push('/outlines')}
                            whileHover={{scale: 1.02}}
                            whileTap={{scale: 0.98}}
                            className="
                inline-flex items-center gap-2
                px-4 py-2 rounded-lg
                text-white font-medium text-sm
                bg-gradient-to-r from-blue-600 to-blue-500
                hover:from-blue-700 hover:to-blue-600
                shadow-md hover:shadow-lg
                transition-shadow duration-200
              "
                        >
                            <Plus className="w-4 h-4" />
                            <span>从大纲创建</span>
                        </motion.button>
                    </div>
                </div>
            </nav>

            {/* 主内容区域 */}
            <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* 页面标题 */}
                <motion.div
                    initial={{opacity: 0, y: -10}}
                    animate={{opacity: 1, y: 0}}
                    className="mb-8"
                >
                    <h2 className="text-2xl font-bold text-[var(--color-text)]">
            我的 PPT
                    </h2>
                    <p className="mt-1 text-[var(--color-text-muted)]">
            管理和编辑您的演示文稿
                    </p>
                </motion.div>

                {/* 错误提示 */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{opacity: 0, height: 0}}
                            animate={{opacity: 1, height: 'auto'}}
                            exit={{opacity: 0, height: 0}}
                            className="mb-6"
                        >
                            <div className="alert-error alert-error-icon">
                                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                <div className="flex-1">
                                    <p>{error}</p>
                                </div>
                                <button
                                    onClick={fetchPresentations}
                                    className="p-1 hover:bg-red-100 rounded transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* 加载状态 */}
                {isLoading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="text-center">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto text-[var(--color-primary)]" />
                            <p className="mt-4 text-[var(--color-text-muted)]">加载中...</p>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* 空状态 */}
                        {presentations.length === 0 && !error ? (
                            <motion.div
                                initial={{opacity: 0, scale: 0.95}}
                                animate={{opacity: 1, scale: 1}}
                                className="text-center py-20"
                            >
                                <div
                                    className="
                    w-20 h-20 mx-auto mb-6
                    bg-[var(--color-surface)] rounded-2xl
                    flex items-center justify-center
                  "
                                >
                                    <Presentation className="w-10 h-10 text-[var(--color-text-placeholder)]" />
                                </div>
                                <h3 className="text-lg font-medium text-[var(--color-text)]">
                  暂无 PPT
                                </h3>
                                <p className="mt-2 text-[var(--color-text-muted)] max-w-md mx-auto">
                  还没有创建任何 PPT。从大纲生成您的第一个演示文稿吧。
                                </p>
                                <motion.button
                                    onClick={() => router.push('/outlines')}
                                    whileHover={{scale: 1.02}}
                                    whileTap={{scale: 0.98}}
                                    className="
                    mt-6 inline-flex items-center gap-2
                    px-5 py-2.5 rounded-lg
                    text-white font-medium
                    bg-gradient-to-r from-blue-600 to-blue-500
                    hover:from-blue-700 hover:to-blue-600
                    shadow-md hover:shadow-lg
                    transition-shadow duration-200
                  "
                                >
                                    <Plus className="w-4 h-4" />
                                    <span>从大纲创建</span>
                                </motion.button>
                            </motion.div>
                        ) : (
                        /* PPT 列表 */
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                            >
                                <AnimatePresence>
                                    {presentations.map((presentation) => (
                                        <motion.div
                                            key={presentation.id}
                                            variants={itemVariants}
                                            layout
                                            className="
                        bg-white rounded-xl
                        border border-[var(--color-border)]
                        hover:shadow-lg hover:border-[var(--color-primary)]
                        transition-all duration-300
                        overflow-hidden
                      "
                                        >
                                            {/* 卡片头部 */}
                                            <div className="p-5 border-b border-[var(--color-border)]">
                                                <div className="flex items-start justify-between">
                                                    <h3 className="font-semibold text-[var(--color-text)] line-clamp-2 pr-2">
                                                        {presentation.title}
                                                    </h3>
                                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusMap[presentation.status].color}`}>
                                                        {statusMap[presentation.status].label}
                                                    </span>
                                                </div>
                                                <p className="mt-2 text-sm text-[var(--color-text-muted)] line-clamp-2">
                                                    {presentation.description || '暂无描述'}
                                                </p>
                                            </div>

                                            {/* 卡片内容 */}
                                            <div className="p-5">
                                                <div className="flex items-center gap-4 text-sm text-[var(--color-text-muted)] mb-4">
                                                    <span className="flex items-center gap-1">
                                                        <Layers className="w-4 h-4" />
                                                        {presentation.slideCount} 页
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <FileText className="w-4 h-4" />
                            v{presentation.version}
                                                    </span>
                                                </div>

                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-[var(--color-text-muted)] flex items-center gap-1">
                                                        <Clock className="w-3 h-3" />
                                                        {formatDate(presentation.createdAt)}
                                                    </span>

                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => handleEdit(presentation)}
                                                            className="
                                px-3 py-1.5 rounded-lg
                                text-sm font-medium
                                text-[var(--color-primary)]
                                hover:bg-blue-50
                                transition-colors
                              "
                                                        >
                              编辑
                                                        </button>
                                                        <button
                                                            onClick={() => handleDelete(presentation)}
                                                            disabled={deleteLoading === presentation.id}
                                                            className="
                                px-3 py-1.5 rounded-lg
                                text-sm font-medium
                                text-red-600
                                hover:bg-red-50
                                transition-colors
                                disabled:opacity-50
                              "
                                                        >
                                                            {deleteLoading === presentation.id ? (
                                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                            ) : (
                                                                '删除'
                                                            )}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            </motion.div>
                        )}
                    </>
                )}
            </main>
        </div>
    );
}
