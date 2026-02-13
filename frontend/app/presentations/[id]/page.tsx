'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Loader2, 
  Save, 
  Trash2, 
  LayoutTemplate,
  Palette,
  Wand2,
  FileText,
  Image as ImageIcon,
  Type
} from 'lucide-react';
import { 
  getPresentation, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  updatePresentation, 
  deletePresentation,
  addSlide,
  updateSlide,
  deleteSlide,
  undoSlide,
  redoSlide
} from '@/lib/api/presentations';
import { PresentationDetailResponse, Slide, SlideType, SlideContent } from '@/types/presentation';
import { AxiosError } from 'axios';
import SlideThumbnail from '@/components/presentations/SlideThumbnail';
import SlideEditor from '@/components/presentations/SlideEditor';
import SlideToolbar from '@/components/presentations/SlideToolbar';
import ExportButton from '@/components/presentations/ExportButton';

// 生成唯一 ID
function generateId(): string {
  return `slide-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// 默认AI生成的插图提示词
function generateDefaultImagePrompt(slideTitle: string, slideType: SlideType): string {
  const typePrompts: Record<SlideType, string> = {
    title: '高端商务封面背景，简洁大气，渐变光影',
    content: '专业商务场景配图，清晰现代风格',
    section: '章节分隔背景，视觉层次分明',
    chart: '数据可视化背景，科技感配色',
    conclusion: '总结页背景，温暖专业氛围',
  };
  return `${typePrompts[slideType]}，主题：${slideTitle}`;
}

// 创建默认幻灯片
function createDefaultSlide(index: number): Slide {
  return {
    id: generateId(),
    type: 'content',
    content: {
      title: `第 ${index + 1} 页`,
      text: '',
      bullets: [],
    },
    orderIndex: index,
    imagePrompt: generateDefaultImagePrompt(`第 ${index + 1} 页`, 'content'),
  };
}

export default function PresentationEditorPage() {
  const params = useParams();
  const router = useRouter();
  const presentationId = params.id as string;

  const [presentation, setPresentation] = useState<PresentationDetailResponse | null>(null);
  const [slides, setSlides] = useState<Slide[]>([]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  
  // 撤销重做历史
  const [history, setHistory] = useState<Slide[][]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  useEffect(() => {
    fetchPresentation();
  }, [presentationId, fetchPresentation]);

  const fetchPresentation = useCallback(async () => {
    try {
      const data = await getPresentation(presentationId);
      setPresentation(data);
      setTitle(data.title);
      setDescription(data.description || '');
      const sortedSlides = [...data.slides].sort((a, b) => a.orderIndex - b.orderIndex);
      setSlides(sortedSlides);
      
      // 初始化历史
      setHistory([sortedSlides]);
      setHistoryIndex(0);
    } catch (err) {
      const axiosError = err as AxiosError;
      if (axiosError.response?.status === 401) {
        router.push('/login');
      } else if (axiosError.response?.status === 404) {
        setError('PPT 不存在');
      } else {
        setError('获取 PPT 失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  }, [presentationId, router]);

  // 保存历史状态
  const saveToHistory = useCallback((newSlides: Slide[]) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push([...newSlides]);
    // 限制历史记录数量
    if (newHistory.length > 50) {
      newHistory.shift();
    }
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  }, [history, historyIndex]);

  // 撤销
  const handleUndo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setSlides([...history[newIndex]]);
    }
  };

  // 重做
  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setSlides([...history[newIndex]]);
    }
  };

  // 添加幻灯片
  const handleAddSlide = () => {
    const newSlide = createDefaultSlide(slides.length);
    const newSlides = [...slides];
    // 在当前幻灯片后插入
    const insertIndex = currentSlideIndex + 1;
    newSlides.splice(insertIndex, 0, newSlide);
    // 重新排序
    newSlides.forEach((slide, index) => {
      slide.orderIndex = index;
    });
    setSlides(newSlides);
    setCurrentSlideIndex(insertIndex);
    saveToHistory(newSlides);
  };

  // 删除幻灯片
  const handleDeleteSlide = () => {
    if (slides.length <= 1) {
      alert('至少需要保留一页幻灯片');
      return;
    }
    if (!confirm('确定要删除当前幻灯片吗？')) return;
    
    const newSlides = slides.filter((_, i) => i !== currentSlideIndex);
    newSlides.forEach((slide, index) => {
      slide.orderIndex = index;
    });
    setSlides(newSlides);
    setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1));
    saveToHistory(newSlides);
  };

  // 更新幻灯片内容
  const handleUpdateSlideContent = (contentUpdates: Partial<SlideContent>) => {
    const newSlides = [...slides];
    const currentSlide = newSlides[currentSlideIndex];
    newSlides[currentSlideIndex] = {
      ...currentSlide,
      content: {
        ...currentSlide.content,
        ...contentUpdates,
      },
    };
    setSlides(newSlides);
    saveToHistory(newSlides);
  };

  // 更新幻灯片类型
  const handleUpdateSlideType = (type: SlideType) => {
    const newSlides = [...slides];
    const currentSlide = newSlides[currentSlideIndex];
    newSlides[currentSlideIndex] = {
      ...currentSlide,
      type,
      // 重置内容以适配新类型
      content: {
        title: currentSlide.content.title,
        subtitle: type === 'title' ? currentSlide.content.subtitle : undefined,
        text: ['content', 'conclusion'].includes(type) ? currentSlide.content.text || '' : undefined,
        bullets: ['content', 'conclusion'].includes(type) ? currentSlide.content.bullets || [] : undefined,
        description: ['section', 'chart'].includes(type) ? currentSlide.content.description : undefined,
      },
    };
    setSlides(newSlides);
    saveToHistory(newSlides);
  };

  // 保存 PPT
  const handleSave = async () => {
    if (!title.trim()) {
      setError('标题不能为空');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await updatePresentation(presentationId, {
        title: title.trim(),
        description: description.trim() || undefined,
        slides: slides.map((slide, index) => ({
          ...slide,
          orderIndex: index,
        })),
      });
      // 显示成功提示
      // 实际项目中可以使用 toast 通知
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

  // 删除 PPT
  const handleDelete = async () => {
    if (!confirm('确定要删除这个 PPT 吗？此操作不可恢复。')) return;

    try {
      await deletePresentation(presentationId);
      router.push('/presentations');
    } catch (err) {
      const axiosError = err as AxiosError;
      if (axiosError.response?.status === 401) {
        router.push('/login');
      } else {
        alert('删除失败：' + ((axiosError.response?.data as { message?: string })?.message || '请稍后重试'));
      }
    }
  };

  // 上一页
  const handlePrevSlide = () => {
    setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1));
  };

  // 下一页
  const handleNextSlide = () => {
    setCurrentSlideIndex(Math.min(slides.length - 1, currentSlideIndex + 1));
  };

  // 导出功能已由 ExportButton 组件处理
  const handleExport = () => {
    // ExportButton 组件已集成导出功能
  };

  // 预览功能
  const handlePreview = () => {
    // 在新标签页打开预览
    window.open(`/presentations/${presentationId}/preview`, '_blank');
  };

  // 获取当前幻灯片
  const currentSlide = slides[currentSlideIndex];

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[var(--color-primary)]" />
      </div>
    );
  }

  if (error && !presentation) {
    return (
      <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--color-text-muted)]">{error}</p>
          <button
            onClick={() => router.push('/presentations')}
            className="mt-4 text-[var(--color-primary)] hover:underline"
          >
            返回列表
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b border-[var(--color-border)] flex-shrink-0">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/presentations')}
                className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>返回</span>
              </button>

              <div className="h-6 w-px bg-[var(--color-border)]" />

              <div className="flex flex-col">
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="font-semibold text-[var(--color-text)] bg-transparent border-none focus:outline-none focus:ring-0 p-0 text-lg"
                  placeholder="PPT 标题"
                />
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="text-xs text-[var(--color-text-muted)] bg-transparent border-none focus:outline-none focus:ring-0 p-0"
                  placeholder="描述（可选）"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <ExportButton presentationId={presentationId} />
              
              <div className="h-6 w-px bg-[var(--color-border)]" />
              
              <button
                onClick={handleDelete}
                className="
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  text-red-600 hover:bg-red-50
                  transition-colors
                "
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">删除</span>
              </button>

              <motion.button
                onClick={handleSave}
                disabled={saving}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  text-white font-medium
                  bg-gradient-to-r from-blue-600 to-blue-500
                  hover:from-blue-700 hover:to-blue-600
                  shadow-md hover:shadow-lg
                  transition-shadow duration-200
                  disabled:opacity-50
                "
              >
                <Save className={`w-4 h-4 ${saving ? 'animate-pulse' : ''}`} />
                <span>{saving ? '保存中...' : '保存'}</span>
              </motion.button>
            </div>
          </div>
        </div>
      </nav>

      {/* 错误提示 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-50 border-b border-red-200"
          >
            <div className="max-w-[1600px] mx-auto px-4 py-3 text-red-700 text-sm">
              {error}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主编辑区域 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：幻灯片缩略图列表 */}
        <aside className="w-64 bg-gray-50 border-r border-[var(--color-border)] overflow-y-auto flex-shrink-0">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">幻灯片</h3>
              <span className="text-xs text-gray-500">共 {slides.length} 页</span>
            </div>

            <div className="space-y-3">
              {slides.map((slide, index) => (
                <SlideThumbnail
                  key={slide.id}
                  slide={slide}
                  index={index}
                  isActive={index === currentSlideIndex}
                  onClick={() => setCurrentSlideIndex(index)}
                />
              ))}
            </div>
          </div>
        </aside>

        {/* 中央：幻灯片编辑区 */}
        <main className="flex-1 overflow-y-auto bg-gray-100">
          <div className="max-w-4xl mx-auto py-8 px-6">
            {currentSlide && (
              <motion.div
                key={currentSlide.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <SlideEditor
                  slide={currentSlide}
                  onUpdate={handleUpdateSlideContent}
                  onTypeChange={handleUpdateSlideType}
                />
              </motion.div>
            )}
          </div>
        </main>

        {/* 右侧：属性面板 */}
        <aside className="w-72 bg-white border-l border-[var(--color-border)] overflow-y-auto flex-shrink-0">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">属性面板</h3>

            {/* 布局选择 */}
            <div className="mb-6">
              <label className="text-xs font-medium text-gray-500 mb-2 block">页面布局</label>
              <div className="grid grid-cols-2 gap-2">
                {['标准', '分栏', '全图', '数据'].map((layout) => (
                  <button
                    key={layout}
                    className="
                      p-3 rounded-lg border border-gray-200
                      text-xs text-gray-600
                      hover:border-blue-400 hover:text-blue-600
                      transition-colors
                      flex flex-col items-center gap-1
                    "
                  >
                    <LayoutTemplate className="w-5 h-5" />
                    {layout}
                  </button>
                ))}
              </div>
            </div>

            {/* 主题选择 */}
            <div className="mb-6">
              <label className="text-xs font-medium text-gray-500 mb-2 block">主题配色</label>
              <div className="flex gap-2">
                {['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#6B7280'].map((color) => (
                  <button
                    key={color}
                    className="w-8 h-8 rounded-full border-2 border-white shadow-sm hover:scale-110 transition-transform"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>

            {/* 插图提示词 */}
            {currentSlide?.imagePrompt && (
              <div className="mb-6">
                <label className="text-xs font-medium text-gray-500 mb-2 block flex items-center gap-1">
                  <ImageIcon className="w-3 h-3" />
                  插图提示词
                </label>
                <div className="p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
                  {currentSlide.imagePrompt}
                </div>
              </div>
            )}

            {/* AI 辅助 */}
            <div className="border-t pt-4">
              <label className="text-xs font-medium text-gray-500 mb-2 block">AI 辅助</label>
              <button
                className="
                  w-full py-2 px-3 rounded-lg
                  bg-gradient-to-r from-purple-600 to-blue-600
                  text-white text-sm font-medium
                  hover:from-purple-700 hover:to-blue-700
                  transition-colors
                  flex items-center justify-center gap-2
                "
              >
                <Wand2 className="w-4 h-4" />
                优化内容
              </button>
              <p className="mt-2 text-[10px] text-gray-400 text-center">
                使用 AI 优化当前页面内容
              </p>
            </div>
          </div>
        </aside>
      </div>

      {/* 底部工具栏 */}
      <SlideToolbar
        currentSlideIndex={currentSlideIndex}
        totalSlides={slides.length}
        canUndo={historyIndex > 0}
        canRedo={historyIndex < history.length - 1}
        onUndo={handleUndo}
        onRedo={handleRedo}
        onAddSlide={handleAddSlide}
        onDeleteSlide={handleDeleteSlide}
        onPrevSlide={handlePrevSlide}
        onNextSlide={handleNextSlide}
        onSave={handleSave}
        onExport={handleExport}
        onPreview={handlePreview}
        saving={saving}
      />
    </div>
  );
}
