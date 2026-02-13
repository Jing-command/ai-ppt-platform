'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, CheckCircle2, XCircle, Activity } from 'lucide-react';
import { testConnector, testConnectorConfig } from '@/lib/api/connectors';
import { TestConnectorResponse } from '@/types/connector';

interface TestConnectionButtonProps {
  connectorId?: string;
  type?: string;
  config?: Record<string, any>;
  onTestResult?: (result: TestConnectorResponse) => void;
  className?: string;
  variant?: 'default' | 'small';
}

export function TestConnectionButton({
  connectorId,
  type,
  config,
  onTestResult,
  className = '',
  variant = 'default',
}: TestConnectionButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TestConnectorResponse | null>(null);
  const [showResult, setShowResult] = useState(false);

  const canTest = connectorId || (type && config);

  const handleTest = async () => {
    if (!canTest || isLoading) return;

    setIsLoading(true);
    setShowResult(false);

    try {
      let response: TestConnectorResponse;

      if (connectorId) {
        // 测试已保存的连接器
        response = await testConnector(connectorId);
      } else if (type && config) {
        // 测试未保存的连接器配置
        response = await testConnectorConfig(type, config);
      } else {
        throw new Error('无法测试连接：缺少必要参数');
      }

      setResult(response);
      setShowResult(true);
      onTestResult?.(response);
    } catch (error) {
      const errorResult: TestConnectorResponse = {
        success: false,
        message: error instanceof Error ? error.message : '测试连接失败',
        errorDetails: error instanceof Error ? error.stack : undefined,
      };
      setResult(errorResult);
      setShowResult(true);
      onTestResult?.(errorResult);
    } finally {
      setIsLoading(false);
    }
  };

  const getButtonStyles = () => {
    if (result?.success) {
      return 'bg-emerald-50 text-emerald-600 border-emerald-200 hover:bg-emerald-100';
    }
    if (result && !result.success) {
      return 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100';
    }
    return 'bg-white text-[var(--color-text-secondary)] border-[var(--color-border)] hover:bg-[var(--color-surface)] hover:border-[var(--color-border-hover)]';
  };

  const getIcon = () => {
    if (isLoading) {
      return <Loader2 className="animate-spin" size={variant === 'small' ? 14 : 16} />;
    }
    if (result?.success) {
      return <CheckCircle2 size={variant === 'small' ? 14 : 16} />;
    }
    if (result && !result.success) {
      return <XCircle size={variant === 'small' ? 14 : 16} />;
    }
    return <Activity size={variant === 'small' ? 14 : 16} />;
  };

  return (
    <div className={className}>      <motion.button
        type="button"
        onClick={handleTest}
        disabled={!canTest || isLoading}
        whileHover={{ scale: canTest && !isLoading ? 1.02 : 1 }}
        whileTap={{ scale: canTest && !isLoading ? 0.98 : 1 }}
        className={`
          inline-flex items-center justify-center gap-2
          font-medium rounded-lg border
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variant === 'small' ? 'px-3 py-1.5 text-xs' : 'px-4 py-2.5 text-sm'}
          ${getButtonStyles()}
        `}
      >
        {getIcon()}
        <span>
          {isLoading ? '测试中...' : result?.success ? '连接成功' : result ? '连接失败' : '测试连接'}
        </span>
        {result?.latencyMs && (
          <span className="text-xs opacity-75">({result.latencyMs}ms)</span>
        )}
      </motion.button>

      {/* 测试结果提示 */}
      <AnimatePresence>
        {showResult && result && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="mt-3 overflow-hidden"
          >
            <div
              className={`
                p-3 rounded-lg text-sm
                ${result.success
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
                }
              `}
            >
              <div className="flex items-start gap-2">
                {result.success ? (
                  <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="font-medium">{result.message}</p>
                  {result.serverVersion && (
                    <p className="text-xs mt-1 opacity-75">服务器版本: {result.serverVersion}</p>
                  )}
                  {result.errorDetails && (
                    <p className="text-xs mt-1 opacity-75 font-mono">{result.errorDetails}</p>
                  )}
                </div>
              </div>
            </div>          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
