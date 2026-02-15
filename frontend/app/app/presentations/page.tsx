'use client';

import {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
  FileText,
  Plus,
  Search,
  Grid,
  List,
  MoreVertical,
  Trash2,
  Edit,
  Copy,
  Download,
  Filter,
  ChevronLeft,
  ChevronRight,
  Clock,
  AlertCircle
} from 'lucide-react';
import {AppLayout} from '@/components/layout/AppLayout';
import {
  getPresentations,
  deletePresentation,
  createPresentation
} from '@/lib/api/presentations';
import {
  PresentationResponse,
  PresentationStatus
} from '@/types/presentation';

const statusOptions: { value: PresentationStatus | ''; label: string }[] = [
  {value: '', label: '全部状态'},
  {value: 'draft', label: '草稿'},
  {value: 'generating', label: '生成中'},
  {value: 'completed', label: '已完成'},
  {value: 'published', label: '已发布'},
  {value: 'archived', label: '已归档'}
];

const sortOptions = [
  {value: 'updatedAt:desc', label: '最近更新'},
  {value: 'updatedAt:asc', label: '最早更新'},
  {value: 'createdAt:desc', label: '最近创建'},
  {value: 'createdAt:asc', label: '最早创建'},
  {value: 'title:asc', label: '名称 A-Z'},
  {value: 'title:desc', label: '名称 Z-A'}
];

function getStatusBadge(status: PresentationStatus) {
  const statusConfig = {
    draft: {label: '草稿', color: 'bg-gray-100 text-gray-700 border-gray-200'},
    generating: {label: '生成中', color: 'bg-yellow-100 text-yellow-700 border-yellow-200'},
    completed: {label: '已完成', color: 'bg-green-100 text-green-700 border-green-200'},
    published: {label: '已发布', color: 'bg-blue-100 text-blue-700 border-blue-200'},
    archived: {label: '已归档', color: 'bg-gray-100 text-gray-700 border-gray-200'}
  };

  const config = statusConfig[status];
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
      {config.label}
    </span>
  );
}

export default function PresentationsPage() {
  const router = useRouter();
  const [presentations, setPresentations] = useState<PresentationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<PresentationStatus | ''>('');
  const [sortBy, setSortBy] = useState('updatedAt:desc');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; ppt: PresentationResponse } | null>(null);

  useEffect(() => {
    loadPresentations();
  }, [page, statusFilter, sortBy]);

  useEffect(() => {
    const handleClickOutside = () => setContextMenu(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const loadPresentations = async () => {
    try {
      setIsLoading(true);
      const response = await getPresentations({
        page,
        pageSize,
        status: statusFilter || undefined
      });

      let data = response.data;

      // Client-side search
      if (searchQuery) {
        data = data.filter(p =>
          p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.description?.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }

      // Client-side sort
      const [field, order] = sortBy.split(':');
      data = [...data].sort((a, b) => {
        let aVal: any = a[field as keyof PresentationResponse];
        let bVal: any = b[field as keyof PresentationResponse];

        if (field === 'title') {
          aVal = (aVal || '').toLowerCase();
          bVal = (bVal || '').toLowerCase();
        }

        if (order === 'asc') {
          return aVal > bVal ? 1 : -1;
        }
        return aVal < bVal ? 1 : -1;
      });

      setPresentations(data);
      setTotalPages(response.meta.totalPages);
    } catch (error) {
      console.error('Failed to load presentations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const response = await createPresentation({
        title: '未命名演示文稿',
        description: ''
      });
      router.push(`/app/presentations/${response.id}/edit`);
    } catch (error) {
      console.error('Failed to create presentation:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个演示文稿吗？')) { return; }

    try {
      await deletePresentation(id);
      setPresentations(prev => prev.filter(p => p.id !== id));
      setContextMenu(null);
    } catch (error) {
      console.error('Failed to delete presentation:', error);
    }
  };

  const handleContextMenu = (e: React.MouseEvent, ppt: PresentationResponse) => {
    e.preventDefault();
    setContextMenu({x: e.clientX, y: e.clientY, ppt});
  };

  const toggleSelection = (id: string) => {
    const newSet = new Set(selectedItems);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedItems(newSet);
  };

  const filteredPresentations = presentations;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-text)]">PPT 管理</h1>
            <p className="mt-1 text-[var(--color-text-muted)]">
              管理您的所有演示文稿
            </p>
          </div>
          <motion.button
            whileHover={{scale: 1.02}}
            whileTap={{scale: 0.98}}
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-md"
          >
            <Plus className="w-5 h-5" />
            新建PPT
          </motion.button>
        </div>

        {/* Filters & Toolbar */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-white p-4 rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)]">
          <div className="flex flex-col sm:flex-row gap-3 flex-1 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-placeholder)]" />
              <input
                type="text"
                placeholder="搜索PPT..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && loadPresentations()}
                className="w-full pl-10 pr-4 py-2 bg-[var(--color-surface)] border border-transparent rounded-lg text-sm text-[var(--color-text)] placeholder-[var(--color-text-placeholder)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-all"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as PresentationStatus | '');
                setPage(1);
              }}
              className="px-3 py-2 bg-[var(--color-surface)] border border-transparent rounded-lg text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-all"
            >
              {statusOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-[var(--color-surface)] border border-transparent rounded-lg text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-all"
            >
              {sortOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 border-l border-[var(--color-border)] pl-4">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'grid'
                  ? 'bg-blue-100 text-blue-600'
                  : 'text-[var(--color-text-muted)] hover:bg-[var(--color-surface)]'
              }`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'list'
                  ? 'bg-blue-100 text-blue-600'
                  : 'text-[var(--color-text-muted)] hover:bg-[var(--color-surface)]'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredPresentations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-xl border border-[var(--color-border)] border-dashed">
            <FileText className="w-16 h-16 text-[var(--color-text-placeholder)] mb-4" />
            <p className="text-lg font-medium text-[var(--color-text)]">暂无演示文稿</p>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">点击上方按钮创建您的第一个PPT</p>
            <motion.button
              whileHover={{scale: 1.02}}
              whileTap={{scale: 0.98}}
              onClick={handleCreate}
              className="mt-4 flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              新建PPT
            </motion.button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredPresentations.map((ppt) => (
              <motion.div
                key={ppt.id}
                layout
                initial={{opacity: 0, scale: 0.95}}
                animate={{opacity: 1, scale: 1}}
                whileHover={{y: -4}}
                onContextMenu={(e) => handleContextMenu(e, ppt)}
                className="group bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-card-hover)] overflow-hidden cursor-pointer transition-all"
                onClick={() => router.push(`/app/presentations/${ppt.id}/edit`)}
              >
                {/* Thumbnail */}
                <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center relative">
                  <FileText className="w-12 h-12 text-white/80" />
                  <div className="absolute top-2 left-2">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(ppt.id)}
                      onClick={(e) => e.stopPropagation()}
                      onChange={() => toggleSelection(ppt.id)}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </div>
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleContextMenu(e, ppt);
                      }}
                      className="p-1.5 bg-white/90 rounded-lg hover:bg-white transition-colors"
                    >
                      <MoreVertical className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>

                {/* Info */}
                <div className="p-4">
                  <h3 className="font-medium text-[var(--color-text)] truncate">
                    {ppt.title}
                  </h3>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1 line-clamp-1">
                    {ppt.description || '无描述'}
                  </p>
                  <div className="flex items-center justify-between mt-3">
                    {getStatusBadge(ppt.status)}
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {ppt.slideCount} 页
                    </span>
                  </div>
                  <div className="flex items-center gap-1 mt-2 text-xs text-[var(--color-text-muted)]">
                    <Clock className="w-3 h-3" />
                    {new Date(ppt.updatedAt).toLocaleDateString('zh-CN')}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] overflow-hidden">
            <table className="w-full">
              <thead className="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedItems.size === filteredPresentations.length && filteredPresentations.length > 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedItems(new Set(filteredPresentations.map(p => p.id)));
                        } else {
                          setSelectedItems(new Set());
                        }
                      }}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[var(--color-text-secondary)]">名称</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[var(--color-text-secondary)]">状态</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[var(--color-text-secondary)]">幻灯片</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[var(--color-text-secondary)]">更新时间</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-[var(--color-text-secondary)]">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]">
                {filteredPresentations.map((ppt) => (
                  <tr
                    key={ppt.id}
                    className="hover:bg-[var(--color-surface)] cursor-pointer transition-colors"
                    onClick={() => router.push(`/app/presentations/${ppt.id}/edit`)}
                    onContextMenu={(e) => handleContextMenu(e, ppt)}
                  >
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedItems.has(ppt.id)}
                        onChange={() => toggleSelection(ppt.id)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                          <FileText className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="font-medium text-[var(--color-text)]">{ppt.title}</p>
                          <p className="text-sm text-[var(--color-text-muted)]">{ppt.description || '无描述'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(ppt.status)}</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">{ppt.slideCount} 页</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-muted)]">
                      {new Date(ppt.updatedAt).toLocaleString('zh-CN')}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleContextMenu(e, ppt);
                        }}
                        className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
                      >
                        <MoreVertical className="w-4 h-4 text-[var(--color-text-muted)]" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)]">
            <span className="text-sm text-[var(--color-text-muted)]">
              共 {totalPages} 页
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 hover:bg-[var(--color-surface)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="px-4 py-2 text-sm font-medium text-[var(--color-text)]">
                {page}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 hover:bg-[var(--color-surface)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Context Menu */}
      <AnimatePresence>
        {contextMenu && (
          <motion.div
            initial={{opacity: 0, scale: 0.95}}
            animate={{opacity: 1, scale: 1}}
            exit={{opacity: 0, scale: 0.95}}
            style={{top: contextMenu.y, left: contextMenu.x}}
            className="fixed z-50 w-48 bg-white rounded-lg shadow-lg border border-[var(--color-border)] py-1"
          >
            <button
              onClick={() => {
                router.push(`/app/presentations/${contextMenu.ppt.id}/edit`);
                setContextMenu(null);
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-surface)] transition-colors"
            >
              <Edit className="w-4 h-4" />
              编辑
            </button>
            <button
              onClick={() => {
                // Duplicate logic
                setContextMenu(null);
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-surface)] transition-colors"
            >
              <Copy className="w-4 h-4" />
              复制
            </button>
            <button
              onClick={() => {
                // Export logic
                setContextMenu(null);
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-surface)] transition-colors"
            >
              <Download className="w-4 h-4" />
              导出
            </button>
            <div className="border-t border-[var(--color-border)] my-1" />
            <button
              onClick={() => handleDelete(contextMenu.ppt.id)}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              删除
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  );
}
