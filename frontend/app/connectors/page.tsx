'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Database, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Connector } from '@/types/connector';
import {
  getConnectors,
  deleteConnector,
} from '@/lib/api/connectors';
import { ConnectorCard } from '@/components/connectors/ConnectorCard';
import { AxiosError } from 'axios';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

export default function ConnectorsPage() {
  const router = useRouter();
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [, setDeleteLoading] = useState<string | null>(null);

  const fetchConnectors = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await getConnectors(1, 100);
      setConnectors(response.data);
    } catch (err) {
      const axiosError = err as AxiosError;
      if (axiosError.response?.status === 401) {
        setError('请先登录');
        router.push('/login');
      } else {
        setError('获取连接器列表失败，请稍后重试');
      }
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchConnectors();
  }, [fetchConnectors]);

  const handleEdit = (_connector: Connector) => {
    // 编辑功能 - 可以导航到编辑页面或打开编辑弹窗
    // 这里暂时使用 alert，实际应该实现编辑页面
    alert(`编辑连接器: ${_connector.name}\n功能开发中...`);
  };

  const handleDelete = async (connector: Connector) => {
    if (!confirm(`确定要删除连接器 "${connector.name}" 吗？此操作不可恢复。`)) {
      return;
    }

    setDeleteLoading(connector.id);

    try {
      await deleteConnector(connector.id);
      setConnectors((prev) => prev.filter((c) => c.id !== connector.id));
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

  const handleTest = () => {
    // 刷新连接器数据
    fetchConnectors();
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
              <h1 className="text-lg font-semibold text-[var(--color-text)]">连接器管理</h1>
            </div>

            <motion.button
              onClick={() => router.push('/connectors/new')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
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
              <span>添加连接器</span>
            </motion.button>
          </div>
        </div>
      </nav>

      {/* 主内容区域 */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-[var(--color-text)]">
            数据源连接器
          </h2>
          <p className="mt-1 text-[var(--color-text-muted)]">
            管理您的数据库和第三方服务连接，用于生成数据驱动的 PPT
          </p>
        </motion.div>

        {/* 错误提示 */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <div className="alert-error alert-error-icon">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <div className="flex-1">
                  <p>{error}</p>
                </div>
                <button
                  onClick={fetchConnectors}
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
            {connectors.length === 0 && !error ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-20"
              >
                <div
                  className="
                    w-20 h-20 mx-auto mb-6
                    bg-[var(--color-surface)] rounded-2xl
                    flex items-center justify-center
                  "
                >
                  <Database className="w-10 h-10 text-[var(--color-text-placeholder)]" />
                </div>
                <h3 className="text-lg font-medium text-[var(--color-text)]">
                  暂无连接器
                </h3>
                <p className="mt-2 text-[var(--color-text-muted)] max-w-md mx-auto">
                  还没有配置任何数据源连接器。添加一个连接器，开始从数据库或第三方服务获取数据生成 PPT。
                </p>
                <motion.button
                  onClick={() => router.push('/connectors/new')}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
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
                  <span>添加第一个连接器</span>
                </motion.button>
              </motion.div>
            ) : (
              /* 连接器列表 */
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                <AnimatePresence>
                  {connectors.map((connector) => (
                    <ConnectorCard
                      key={connector.id}
                      connector={connector}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                      onTest={handleTest}
                    />
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
