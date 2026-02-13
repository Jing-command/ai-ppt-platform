'use client';

import { motion } from 'framer-motion';
import { Database, Cloud, MoreHorizontal, Edit2, Trash2, Activity, Calendar } from 'lucide-react';
import { Connector, getConnectorDisplayStatus, getConnectorTypeLabel, ConnectorType } from '@/types/connector';
import { TestConnectionButton } from './TestConnectionButton';

interface ConnectorCardProps {
  connector: Connector;
  onEdit: (connector: Connector) => void;
  onDelete: (connector: Connector) => void;
  onTest: (connector: Connector) => void;
}

const typeIcons: Record<ConnectorType, React.ReactNode> = {
  mysql: <Database className="w-5 h-5" />,
  postgresql: <Database className="w-5 h-5" />,
  mongodb: <Database className="w-5 h-5" />,
  salesforce: <Cloud className="w-5 h-5" />,
  csv: <Database className="w-5 h-5" />,
  api: <Cloud className="w-5 h-5" />,
};

const typeColors: Record<ConnectorType, { bg: string; text: string }> = {
  mysql: { bg: 'bg-blue-50', text: 'text-blue-600' },
  postgresql: { bg: 'bg-indigo-50', text: 'text-indigo-600' },
  mongodb: { bg: 'bg-green-50', text: 'text-green-600' },
  salesforce: { bg: 'bg-sky-50', text: 'text-sky-600' },
  csv: { bg: 'bg-orange-50', text: 'text-orange-600' },
  api: { bg: 'bg-purple-50', text: 'text-purple-600' },
};

export function ConnectorCard({ connector, onEdit, onDelete, onTest }: ConnectorCardProps) {
  const displayStatus = getConnectorDisplayStatus(connector);
  const typeLabel = getConnectorTypeLabel(connector.type);
  const typeColor = typeColors[connector.type] || { bg: 'bg-gray-50', text: 'text-gray-600' };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '从未';
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3, ease: "easeOut" as const }}
      className="card p-5 flex flex-col gap-4"
    >
      {/* 头部：图标、名称、类型 */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`
              w-10 h-10 rounded-lg flex items-center justify-center
              ${typeColor.bg} ${typeColor.text}
            `}
          >
            {typeIcons[connector.type] || <Database className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="font-semibold text-[var(--color-text)] text-base">
              {connector.name}
            </h3>
            <p className="text-xs text-[var(--color-text-muted)]">
              {typeLabel}
            </p>
          </div>
        </div>

        {/* 状态指示器 */}
        <div className="flex items-center gap-2">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: displayStatus.color }}
          />
          <span
            className="text-xs font-medium"
            style={{ color: displayStatus.color }}
          >
            {displayStatus.label}
          </span>
        </div>
      </div>

      {/* 描述 */}
      {connector.description && (
        <p className="text-sm text-[var(--color-text-secondary)] line-clamp-2">
          {connector.description}
        </p>
      )}

      {/* 连接信息 */}
      <div className="text-xs text-[var(--color-text-muted)] space-y-1">
        {connector.config?.host && (
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5" />
            <span>{connector.config.host}:{connector.config.port || '默认端口'}</span>
          </div>
        )}
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5" />
          <span>最后测试: {formatDate(connector.lastTestedAt)}</span>
        </div>
      </div>

      {/* 分隔线 */}
      <div className="border-t border-[var(--color-border)]" />

      {/* 操作按钮 */}
      <div className="flex items-center justify-between">
        <TestConnectionButton
          connectorId={connector.id}
          variant="small"
          onTestResult={(result) => {
            if (result.success) {
              onTest(connector);
            }
          }}
        />

        <div className="flex items-center gap-2">
          <motion.button
            onClick={() => onEdit(connector)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="
              p-2 rounded-lg
              text-[var(--color-text-muted)]
              hover:text-[var(--color-primary)]
              hover:bg-blue-50
              transition-colors duration-200
            "
            title="编辑"
          >
            <Edit2 className="w-4 h-4" />
          </motion.button>

          <motion.button
            onClick={() => onDelete(connector)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="
              p-2 rounded-lg
              text-[var(--color-text-muted)]
              hover:text-red-600
              hover:bg-red-50
              transition-colors duration-200
            "
            title="删除"
          >
            <Trash2 className="w-4 h-4" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
