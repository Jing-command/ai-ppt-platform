'use client';

import {useEffect, useState, useCallback} from 'react';
import {useParams, useRouter} from 'next/navigation';
import {motion} from 'framer-motion';
import {
    ArrowLeft, Loader2, Save, Trash2, FileText, Plus,
    ImageIcon, Palette, Wand2, ChevronUp, ChevronDown
} from 'lucide-react';
import {
    getOutline, updateOutline, deleteOutline, createPresentationFromOutline
} from '@/lib/api/outlines';
import {OutlineDetailResponse, OutlineUpdate, OutlineSection, PageType, OutlineBackground} from '@/types/outline';
import {AxiosError} from 'axios';
import BackgroundSettingsModal from '@/components/outlines/BackgroundSettingsModal';

// 页面类型标签
const pageTypeLabels: Record<PageType, string> = {
    title: '封面',
    content: '内容',
    section: '章节页',
    chart: '图表',
    conclusion: '总结'
};

const pageTypeColors: Record<PageType, string> = {
    title: 'bg-purple-100 text-purple-700',
    content: 'bg-blue-100 text-blue-700',
    section: 'bg-orange-100 text-orange-700',
    chart: 'bg-green-100 text-green-700',
    conclusion: 'bg-gray-100 text-gray-700'
};

// 生成唯一 ID
function generateId(): string {
    return `page-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// 默认AI生成的插图提示词（模拟）
function generateDefaultImagePrompt(pageTitle: string, pageType: PageType): string {
    const typePrompts: Record<PageType, string> = {
        title: '高端商务封面背景，简洁大气，渐变光影',
        content: '专业商务场景配图，清晰现代风格',
        section: '章节分隔背景，视觉层次分明',
        chart: '数据可视化背景，科技感配色',
        conclusion: '总结页背景，温暖专业氛围'
    };
    return `${typePrompts[pageType]}，主题：${pageTitle}`;
}

export default function OutlineDetailPage() {
    const params = useParams();
    const router = useRouter();
    const outlineId = params.id as string;

    const [outline, setOutline] = useState<OutlineDetailResponse | null>(null);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [pages, setPages] = useState<OutlineSection[]>([]);
    const [background, setBackground] = useState<OutlineBackground | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState('');
    const [isBgModalOpen, setIsBgModalOpen] = useState(false);
    const [expandedPages, setExpandedPages] = useState<Set<number>>(new Set());


    const fetchOutline = useCallback(async () => {
        try {
            const data = await getOutline(outlineId);
            setOutline(data);
            setTitle(data.title);
            setDescription(data.description || '');
            setPages(data.pages || []);
            setBackground(data.background);

            // 如果没有背景设置，默认使用纯色白色
            if (!data.background) {
                setBackground({type: 'solid', color: '#ffffff'});
            }
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                router.push('/login');
            } else if (axiosError.response?.status === 404) {
                setError('大纲不存在');
            } else {
                setError('获取大纲失败，请稍后重试');
            }
        } finally {
            setLoading(false);
        }
    }, [outlineId, router]);

    const togglePageExpand = (index: number) => {
        const newExpanded = new Set(expandedPages);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedPages(newExpanded);
    };

    useEffect(() => {
        fetchOutline();
    }, [outlineId, fetchOutline]);

    const handleAddPage = (index?: number) => {
        const newPage: OutlineSection = {
            id: generateId(),
            pageNumber: pages.length + 1,
            title: `第 ${pages.length + 1} 页`,
            content: '',
            pageType: 'content',
            imagePrompt: generateDefaultImagePrompt(`第 ${pages.length + 1} 页`, 'content')
        };

        if (index !== undefined) {
            const newPages = [...pages];
            newPages.splice(index + 1, 0, newPage);
            // 重新计算页码
            newPages.forEach((p, i) => {
                p.pageNumber = i + 1;
            });
            setPages(newPages);
        } else {
            setPages([...pages, newPage]);
        }
    };

    const handleUpdatePage = (index: number, updates: Partial<OutlineSection>) => {
        const newPages = [...pages];
        newPages[index] = {...newPages[index], ...updates};

        // 如果更新了标题或类型，且没有自定义插图提示词，则重新生成
        if ((updates.title || updates.pageType) && !newPages[index].imagePrompt?.includes('自定义')) {
            newPages[index].imagePrompt = generateDefaultImagePrompt(
                newPages[index].title,
                newPages[index].pageType || 'content'
            );
        }

        setPages(newPages);
    };

    const handleDeletePage = (index: number) => {
        if (!confirm('确定要删除这一页吗？')) { return; }
        const newPages = pages.filter((_, i) => i !== index);
        // 重新计算页码
        newPages.forEach((p, i) => {
            p.pageNumber = i + 1;
        });
        setPages(newPages);
    };

    const handleMovePage = (index: number, direction: 'up' | 'down') => {
        if (direction === 'up' && index === 0) { return; }
        if (direction === 'down' && index === pages.length - 1) { return; }

        const newPages = [...pages];
        const targetIndex = direction === 'up' ? index - 1 : index + 1;
        [newPages[index], newPages[targetIndex]] = [newPages[targetIndex], newPages[index]];

        // 重新计算页码
        newPages.forEach((p, i) => {
            p.pageNumber = i + 1;
        });
        setPages(newPages);
    };

    const handleRegenerateImagePrompt = (index: number) => {
        const page = pages[index];
        const newPrompt = generateDefaultImagePrompt(page.title, page.pageType || 'content');
        handleUpdatePage(index, {imagePrompt: newPrompt});
    };

    const handleSave = async () => {
        if (!title.trim()) {
            setError('标题不能为空');
            return;
        }

        setSaving(true);
        setError('');

        try {
            const data: OutlineUpdate = {
                title: title.trim(),
                description: description.trim() || undefined,
                pages: pages.map((p, idx) => ({
                    ...p,
                    pageNumber: idx + 1
                })),
                background
            };

            await updateOutline(outlineId, data);
            alert('保存成功！');
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                router.push('/login');
            } else {
                setError((axiosError.response?.data as { message?: string })?.message || '保存失败');
            }
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm('确定要删除这个大纲吗？此操作不可恢复。')) { return; }

        try {
            await deleteOutline(outlineId);
            router.push('/outlines');
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                router.push('/login');
            } else {
                alert('删除失败：' + ((axiosError.response?.data as { message?: string })?.message || '请稍后重试'));
            }
        }
    };

    const handleCreatePresentation = async () => {
        if (pages.length === 0) {
            setError('请至少添加一页内容');
            return;
        }

        setCreating(true);
        setError('');

        try {
            await createPresentationFromOutline(outlineId, {
                generateContent: true
            });
            alert('PPT 创建任务已提交！');
            router.push('/presentations');
        } catch (err) {
            const axiosError = err as AxiosError;
            if (axiosError.response?.status === 401) {
                router.push('/login');
            } else {
                setError((axiosError.response?.data as { message?: string })?.message || '创建 PPT 失败');
            }
        } finally {
            setCreating(false);
        }
    };

    const getBackgroundPreview = () => {
        if (!background) { return '#ffffff'; }

        switch (background.type) {
        case 'solid':
            return background.color || '#ffffff';
        case 'upload':
            return background.url ? `url(${background.url})` : '#f3f4f6';
        case 'ai':
            return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'; // AI生成的占位渐变
        default:
            return '#ffffff';
        }
    };

    const getBackgroundLabel = () => {
        if (!background) { return '未设置'; }

        switch (background.type) {
        case 'ai':
            return 'AI生成';
        case 'upload':
            return '自定义图片';
        case 'solid':
            return '纯色';
        default:
            return '未设置';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-[var(--color-primary)]" />
            </div>
        );
    }

    if (error && !outline) {
        return (
            <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
                <div className="text-center">
                    <p className="text-[var(--color-text-muted)]">{error}</p>
                    <button
                        onClick={() => router.push('/outlines')}
                        className="mt-4 text-[var(--color-primary)] hover:underline"
                    >
            返回列表
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[var(--color-background)]">
            {/* 导航栏 */}
            <nav className="bg-white shadow-sm border-b border-[var(--color-border)]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <button
                            onClick={() => router.push('/outlines')}
                            className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            <span>返回大纲列表</span>
                        </button>

                        <div className="flex gap-2">
                            <button
                                onClick={() => setIsBgModalOpen(true)}
                                className="
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  text-blue-600 hover:bg-blue-50
                  transition-colors
                "
                            >
                                <Palette className="w-4 h-4" />
                背景设置
                            </button>
                            <button
                                onClick={handleDelete}
                                className="
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  text-red-600 hover:bg-red-50
                  transition-colors
                "
                            >
                                <Trash2 className="w-4 h-4" />
                删除
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* 主内容 */}
            <main className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    className="space-y-6"
                >
                    {/* 错误提示 */}
                    {error && (
                        <div className="alert-error">{error}</div>
                    )}

                    {/* 基本信息卡片 */}
                    <div className="bg-white rounded-xl border border-[var(--color-border)] shadow-sm p-6">
                        <div className="space-y-4">
                            <div>
                                <label className="label-text">大纲标题</label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    className="input-field"
                                    placeholder="输入大纲标题"
                                />
                            </div>

                            <div>
                                <label className="label-text">描述</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="input-field resize-none"
                                    rows={2}
                                    placeholder="输入大纲描述（可选）"
                                />
                            </div>
                        </div>
                    </div>

                    {/* 背景预览卡片 */}
                    <div className="bg-white rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
                        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Palette className="w-5 h-5 text-blue-600" />
                                <span className="font-medium">PPT背景</span>
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                                    {getBackgroundLabel()}
                                </span>
                            </div>
                            <button
                                onClick={() => setIsBgModalOpen(true)}
                                className="text-sm text-blue-600 hover:underline"
                            >
                修改
                            </button>
                        </div>
                        <div
                            className="h-24 w-full flex items-center justify-center"
                            style={{
                                background: getBackgroundPreview(),
                                backgroundSize: 'cover',
                                backgroundPosition: 'center',
                                opacity: background?.opacity ?? 1,
                                filter: background?.blur ? `blur(${background.blur}px)` : undefined
                            }}
                        >
                            <span className="text-gray-400 text-sm bg-white/80 px-3 py-1 rounded">
                背景预览
                            </span>
                        </div>
                    </div>

                    {/* 页面列表 */}
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <h2 className="text-lg font-semibold text-[var(--color-text)]">页面规划</h2>
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  共 {pages.length} 页
                                </span>
                            </div>
                            <button
                                onClick={() => handleAddPage()}
                                className="
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  text-[var(--color-primary)] hover:bg-blue-50
                  transition-colors
                "
                            >
                                <Plus className="w-4 h-4" />
                添加页面
                            </button>
                        </div>

                        <div className="space-y-3">
                            {pages.map((page, index) => (
                                <motion.div
                                    key={page.id}
                                    initial={{opacity: 0, x: -20}}
                                    animate={{opacity: 1, x: 0}}
                                    transition={{delay: index * 0.03}}
                                    className="
                    bg-white rounded-xl border border-[var(--color-border)]
                    shadow-sm overflow-hidden
                  "
                                >
                                    <div className="p-4">
                                        <div className="flex items-start gap-4">
                                            {/* 页码和操作 */}
                                            <div className="flex flex-col items-center gap-1 pt-1">
                                                <span className="text-2xl font-bold text-blue-600 w-10 text-center">
                                                    {page.pageNumber}
                                                </span>
                                                <div className="flex flex-col gap-0.5">
                                                    <button
                                                        onClick={() => handleMovePage(index, 'up')}
                                                        disabled={index === 0}
                                                        className="p-0.5 text-gray-400 hover:text-blue-500 disabled:opacity-30 rounded"
                                                    >
                                                        <ChevronUp className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleMovePage(index, 'down')}
                                                        disabled={index === pages.length - 1}
                                                        className="p-0.5 text-gray-400 hover:text-blue-500 disabled:opacity-30 rounded"
                                                    >
                                                        <ChevronDown className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="flex-1 space-y-3">
                                                {/* 页面标题和类型 */}
                                                <div className="flex items-center gap-3">
                                                    <select
                                                        value={page.pageType || 'content'}
                                                        onChange={(e) => handleUpdatePage(index, {pageType: e.target.value as PageType})}
                                                        className={`px-2 py-1 rounded text-xs font-medium ${pageTypeColors[page.pageType || 'content']}`}
                                                    >
                                                        {Object.entries(pageTypeLabels).map(([type, label]) => (
                                                            <option key={type} value={type}>{label}</option>
                                                        ))}
                                                    </select>

                                                    <input
                                                        type="text"
                                                        value={page.title}
                                                        onChange={(e) => handleUpdatePage(index, {title: e.target.value})}
                                                        className="flex-1 font-medium bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-2 py-1"
                                                        placeholder="页面标题"
                                                    />
                                                </div>

                                                {/* 页面内容 */}
                                                <textarea
                                                    value={page.content || ''}
                                                    onChange={(e) => handleUpdatePage(index, {content: e.target.value})}
                                                    className="w-full text-sm text-[var(--color-text-muted)] bg-gray-50 rounded px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    rows={2}
                                                    placeholder="这一页的主要内容..."
                                                />

                                                {/* 展开/收起 插图提示词 */}
                                                <div className="border border-gray-100 rounded-lg overflow-hidden">
                                                    <button
                                                        onClick={() => togglePageExpand(index)}
                                                        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
                                                    >
                                                        <div className="flex items-center gap-2">
                                                            <ImageIcon className="w-4 h-4 text-gray-400" />
                                                            <span className="text-sm text-gray-600">插图提示词</span>
                                                            {page.imagePrompt && (
                                                                <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded">
                                  已设置
                                                                </span>
                                                            )}
                                                        </div>
                                                        <span className="text-gray-400 text-sm">
                                                            {expandedPages.has(index) ? '收起' : '展开'}
                                                        </span>
                                                    </button>

                                                    {expandedPages.has(index) && (
                                                        <div className="p-3 space-y-2">
                                                            <textarea
                                                                value={page.imagePrompt || ''}
                                                                onChange={(e) => handleUpdatePage(index, {imagePrompt: e.target.value})}
                                                                className="w-full text-sm bg-white border border-gray-200 rounded px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                                rows={3}
                                                                placeholder="描述这页PPT需要的插图..."
                                                            />
                                                            <div className="flex justify-between items-center">
                                                                <p className="text-xs text-gray-400">
                                  AI将根据此提示词生成插图
                                                                </p>
                                                                <button
                                                                    onClick={() => handleRegenerateImagePrompt(index)}
                                                                    className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                                                                >
                                                                    <Wand2 className="w-3 h-3" />
                                  重新生成
                                                                </button>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* 演讲备注（可选） */}
                                                <input
                                                    type="text"
                                                    value={page.notes || ''}
                                                    onChange={(e) => handleUpdatePage(index, {notes: e.target.value})}
                                                    className="w-full text-xs text-gray-400 bg-transparent border-b border-dashed border-gray-200 hover:border-gray-400 focus:border-blue-500 focus:outline-none px-3 py-1"
                                                    placeholder="演讲备注（可选）"
                                                />
                                            </div>

                                            {/* 右侧操作 */}
                                            <div className="flex flex-col gap-2">
                                                <button
                                                    onClick={() => handleAddPage(index)}
                                                    className="p-1.5 text-blue-500 hover:bg-blue-50 rounded"
                                                    title="在后面插入新页"
                                                >
                                                    <Plus className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeletePage(index)}
                                                    className="p-1.5 text-red-500 hover:bg-red-50 rounded"
                                                    title="删除这页"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {pages.length === 0 && (
                            <div className="text-center py-12 bg-white rounded-xl border border-dashed border-[var(--color-border)]">
                                <FileText className="w-12 h-12 mx-auto text-[var(--color-text-placeholder)] mb-3" />
                                <p className="text-[var(--color-text-muted)]">暂无页面</p>
                                <button
                                    onClick={() => handleAddPage()}
                                    className="mt-3 text-[var(--color-primary)] hover:underline"
                                >
                  添加第一页
                                </button>
                            </div>
                        )}
                    </div>

                    {/* 操作按钮 */}
                    <div className="flex gap-4 pt-4">
                        <motion.button
                            onClick={handleSave}
                            disabled={saving}
                            whileHover={{scale: 1.01}}
                            whileTap={{scale: 0.99}}
                            className="
                flex-1 py-3 px-4 rounded-lg
                text-white font-medium
                bg-gradient-to-r from-blue-600 to-blue-500
                hover:from-blue-700 hover:to-blue-600
                shadow-md hover:shadow-lg
                transition-shadow duration-200
                disabled:opacity-50
                flex items-center justify-center gap-2
              "
                        >
                            {saving ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                  保存中...
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4" />
                  保存大纲
                                </>
                            )}
                        </motion.button>

                        <motion.button
                            onClick={handleCreatePresentation}
                            disabled={creating || pages.length === 0}
                            whileHover={{scale: 1.01}}
                            whileTap={{scale: 0.99}}
                            className="
                flex-1 py-3 px-4 rounded-lg
                text-white font-medium
                bg-gradient-to-r from-green-600 to-green-500
                hover:from-green-700 hover:to-green-600
                shadow-md hover:shadow-lg
                transition-shadow duration-200
                disabled:opacity-50
                flex items-center justify-center gap-2
              "
                        >
                            {creating ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                  创建中...
                                </>
                            ) : (
                                <>
                                    <FileText className="w-4 h-4" />
                  生成 PPT
                                </>
                            )}
                        </motion.button>
                    </div>
                </motion.div>
            </main>

            {/* 背景设置弹窗 */}
            <BackgroundSettingsModal
                isOpen={isBgModalOpen}
                onClose={() => setIsBgModalOpen(false)}
                background={background}
                onSave={(newBackground) => {
                    setBackground(newBackground);
                    setIsBgModalOpen(false);
                }}
            />
        </div>
    );
}
