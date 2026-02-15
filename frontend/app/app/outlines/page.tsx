'use client';

import {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
  List,
  Plus,
  Search,
  Trash2,
  Edit,
  FileText,
  Sparkles,
  Clock,
  ChevronRight,
  ChevronDown,
  FolderTree,
  X
} from 'lucide-react';
import {AppLayout} from '@/components/layout/AppLayout';
import {
  getOutlines,
  deleteOutline,
  createOutline,
  generateOutline
} from '@/lib/api/outlines';
import {
  OutlineResponse,
  OutlineStatus,
  OutlineGenerateRequest
} from '@/types/outline';

const statusOptions: { value: OutlineStatus | ''; label: string; color: string }[] = [
  {value: '', label: '全部', color: 'bg-gray-100 text-gray-700'},
  {value: 'draft', label: '草稿', color: 'bg-gray-100 text-gray-700'},
  {value: 'generating', label: '生成中', color: 'bg-yellow-100 text-yellow-700'},
  {value: 'completed', label: '已完成', color: 'bg-green-100 text-green-700'},
  {value: 'archived', label: '已归档', color: 'bg-gray-100 text-gray-700'}
];

function getStatusBadge(status: OutlineStatus) {
  const config = statusOptions.find(s => s.value === status);
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${config?.color || 'bg-gray-100'}`}>
      {config?.label || status}
    </span>
  );
}

interface OutlineTreeProps {
  outline: OutlineResponse;
  isExpanded: boolean;
  onToggle: () => void;
}

function OutlineTree({outline, isExpanded, onToggle}: OutlineTreeProps) {
  return (
    <div className="mt-3 pl-4 border-l-2 border-[var(--color-border)]">
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{opacity: 0, height: 0}}
            animate={{opacity: 1, height: 'auto'}}
            exit={{opacity: 0, height: 0}}
            className="space-y-2"
          >
            {outline.pages.map((page, index) => (
              <motion.div
                key={page.id}
                initial={{opacity: 0, x: -10}}
                animate={{opacity: 1, x: 0}}
                transition={{delay: index * 0.05}}
                className="flex items-start gap-3 py-2"
              >
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-medium flex items-center justify-center">
                  {page.pageNumber}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-sm text-[var(--color-text)]">{page.title}</p>
                  {page.content && (
                    <p className="text-xs text-[var(--color-text-muted)] mt-0.5 line-clamp-2">
                      {page.content}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function OutlinesPage() {
  const router = useRouter();
  const [outlines, setOutlines] = useState<OutlineResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<OutlineStatus | ''>('');
  const [expandedOutlines, setExpandedOutlines] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [newOutlineTitle, setNewOutlineTitle] = useState('');
  const [generatePrompt, setGeneratePrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [numSlides, setNumSlides] = useState(15);

  useEffect(() => {
    loadOutlines();
  }, [statusFilter]);

  const loadOutlines = async () => {
    try {
      setIsLoading(true);
      const response = await getOutlines({
        page: 1,
        pageSize: 50,
        status: statusFilter || undefined
      });
      setOutlines(response.data);
    } catch (error) {
      console.error('Failed to load outlines:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateOutline = async () => {
    if (!newOutlineTitle.trim()) { return; }

    try {
      const response = await createOutline({
        title: newOutlineTitle,
        description: '',
        pages: []
      });
      setShowCreateModal(false);
      setNewOutlineTitle('');
      router.push(`/app/outlines/${response.id}/edit`);
    } catch (error) {
      console.error('Failed to create outline:', error);
    }
  };

  const handleGenerateOutline = async () => {
    if (!generatePrompt.trim()) { return; }

    setIsGenerating(true);
    try {
      const request: OutlineGenerateRequest = {
        prompt: generatePrompt,
        numSlides,
        language: 'zh',
        style: 'business'
      };
      const response = await generateOutline(request);

      if (response.taskId) {
        // Poll for completion
        setShowGenerateModal(false);
        setGeneratePrompt('');
        loadOutlines();
      }
    } catch (error) {
      console.error('Failed to generate outline:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteOutline = async (id: string) => {
    if (!confirm('确定要删除这个大纲吗？')) { return; }

    try {
      await deleteOutline(id);
      setOutlines(prev => prev.filter(o => o.id !== id));
    } catch (error) {
      console.error('Failed to delete outline:', error);
    }
  };

  const toggleExpand = (id: string) => {
    const newSet = new Set(expandedOutlines);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedOutlines(newSet);
  };

  const filteredOutlines = outlines.filter(o =>
    o.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-text)]">大纲管理</h1>
            <p className="mt-1 text-[var(--color-text-muted)]">
              管理PPT大纲结构，支持AI智能生成
            </p>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{scale: 1.02}}
              whileTap={{scale: 0.98}}
              onClick={() => setShowGenerateModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all"
            >
              <Sparkles className="w-5 h-5" />
              AI 生成大纲
            </motion.button>
            <motion.button
              whileHover={{scale: 1.02}}
              whileTap={{scale: 0.98}}
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-md"
            >
              <Plus className="w-5 h-5" />
              创建大纲
            </motion.button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center bg-white p-4 rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)]">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-placeholder)]" />
            <input
              type="text"
              placeholder="搜索大纲..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[var(--color-surface)] border border-transparent rounded-lg text-sm text-[var(--color-text)] placeholder-[var(--color-text-placeholder)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-all"
            />
          </div>

          <div className="flex items-center gap-2">
            {statusOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setStatusFilter(opt.value as OutlineStatus | '')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === opt.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredOutlines.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-xl border border-[var(--color-border)] border-dashed">
            <FolderTree className="w-16 h-16 text-[var(--color-text-placeholder)] mb-4" />
            <p className="text-lg font-medium text-[var(--color-text)]">暂无大纲</p>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">创建或生成您的大纲</p>
            <div className="flex items-center gap-3 mt-4">
              <motion.button
                whileHover={{scale: 1.02}}
                whileTap={{scale: 0.98}}
                onClick={() => setShowGenerateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium"
              >
                <Sparkles className="w-4 h-4" />
                AI 生成
              </motion.button>
              <motion.button
                whileHover={{scale: 1.02}}
                whileTap={{scale: 0.98}}
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium"
              >
                <Plus className="w-4 h-4" />
                手动创建
              </motion.button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredOutlines.map((outline) => (
              <motion.div
                key={outline.id}
                initial={{opacity: 0, y: 10}}
                animate={{opacity: 1, y: 0}}
                className="bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] overflow-hidden"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => toggleExpand(outline.id)}
                        className="mt-1 p-1 hover:bg-[var(--color-surface)] rounded transition-colors"
                      >
                        {expandedOutlines.has(outline.id) ? (
                          <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)]" />
                        )}
                      </button>
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="font-medium text-[var(--color-text)]">{outline.title}</h3>
                          {getStatusBadge(outline.status)}
                        </div>
                        {outline.description && (
                          <p className="text-sm text-[var(--color-text-muted)] mt-1">{outline.description}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-[var(--color-text-muted)]">
                          <span className="flex items-center gap-1">
                            <List className="w-3 h-3" />
                            {outline.totalSlides} 页
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(outline.updatedAt).toLocaleDateString('zh-CN')}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => router.push(`/app/outlines/${outline.id}/edit`)}
                        className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
                      >
                        <Edit className="w-4 h-4 text-[var(--color-text-muted)]" />
                      </button>
                      <button
                        onClick={() => {}}
                        className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
                      >
                        <FileText className="w-4 h-4 text-[var(--color-text-muted)]" />
                      </button>
                      <button
                        onClick={() => handleDeleteOutline(outline.id)}
                        className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </div>

                  <OutlineTree
                    outline={outline}
                    isExpanded={expandedOutlines.has(outline.id)}
                    onToggle={() => toggleExpand(outline.id)}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <>
            <div
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setShowCreateModal(false)}
            />
            <motion.div
              initial={{opacity: 0, scale: 0.95}}
              animate={{opacity: 1, scale: 1}}
              exit={{opacity: 0, scale: 0.95}}
              className="fixed inset-0 flex items-center justify-center z-50 p-4"
            >
              <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-[var(--color-text)]">创建大纲</h2>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="p-1 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-[var(--color-text-muted)]" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">
                      大纲标题
                    </label>
                    <input
                      type="text"
                      value={newOutlineTitle}
                      onChange={(e) => setNewOutlineTitle(e.target.value)}
                      placeholder="输入大纲标题..."
                      className="w-full px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                      onKeyDown={(e) => e.key === 'Enter' && handleCreateOutline()}
                    />
                  </div>

                  <motion.button
                    whileHover={{scale: 1.02}}
                    whileTap={{scale: 0.98}}
                    onClick={handleCreateOutline}
                    disabled={!newOutlineTitle.trim()}
                    className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    创建
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <>
            <div
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => !isGenerating && setShowGenerateModal(false)}
            />
            <motion.div
              initial={{opacity: 0, scale: 0.95}}
              animate={{opacity: 1, scale: 1}}
              exit={{opacity: 0, scale: 0.95}}
              className="fixed inset-0 flex items-center justify-center z-50 p-4"
            >
              <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-500" />
                    <h2 className="text-lg font-semibold text-[var(--color-text)]">AI 生成大纲</h2>
                  </div>
                  <button
                    onClick={() => !isGenerating && setShowGenerateModal(false)}
                    disabled={isGenerating}
                    className="p-1 hover:bg-[var(--color-surface)] rounded-lg transition-colors disabled:opacity-50"
                  >
                    <X className="w-5 h-5 text-[var(--color-text-muted)]" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">
                      描述您的主题
                    </label>
                    <textarea
                      value={generatePrompt}
                      onChange={(e) => setGeneratePrompt(e.target.value)}
                      placeholder="例如：一份关于人工智能发展历史的商业演示文稿，面向企业高管，需要包含技术演进、应用场景和未来趋势..."
                      rows={4}
                      disabled={isGenerating}
                      className="w-full px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors resize-none disabled:opacity-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">
                      幻灯片数量: {numSlides}
                    </label>
                    <input
                      type="range"
                      min={3}
                      max={50}
                      value={numSlides}
                      onChange={(e) => setNumSlides(parseInt(e.target.value))}
                      disabled={isGenerating}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-[var(--color-text-muted)] mt-1">
                      <span>3</span>
                      <span>50</span>
                    </div>
                  </div>

                  <motion.button
                    whileHover={{scale: isGenerating ? 1 : 1.02}}
                    whileTap={{scale: isGenerating ? 1 : 0.98}}
                    onClick={handleGenerateOutline}
                    disabled={!generatePrompt.trim() || isGenerating}
                    className="w-full py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white" />
                        生成中...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        开始生成
                      </>
                    )}
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </AppLayout>
  );
}
