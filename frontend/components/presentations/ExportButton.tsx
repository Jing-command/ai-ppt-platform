'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, 
  FileText, 
  Image as ImageIcon,
  X,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronDown
} from 'lucide-react';
import { exportPptx, exportPdf, exportImages, getExportStatus, downloadExport } from '@/lib/api/exports';

interface ExportButtonProps {
  presentationId: string;
}

type ExportFormat = 'pptx' | 'pdf' | 'png' | 'jpg';
type ExportStatus = 'idle' | 'pending' | 'processing' | 'completed' | 'failed';

interface ExportState {
  format: ExportFormat;
  status: ExportStatus;
  progress: number;
  taskId?: string;
  error?: string;
  fileName?: string;
}

const POLLING_INTERVAL = 2000; // 2秒轮询一次

export default function ExportButton({ presentationId }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [exportStates, setExportStates] = useState<Record<ExportFormat, ExportState>>({
    pptx: { format: 'pptx', status: 'idle', progress: 0 },
    pdf: { format: 'pdf', status: 'idle', progress: 0 },
    png: { format: 'png', status: 'idle', progress: 0 },
    jpg: { format: 'jpg', status: 'idle', progress: 0 },
  });
  
  const pollingRefs = useRef<Record<string, NodeJS.Timeout>>({});

  // 清理轮询
  useEffect(() => {
    const timers = pollingRefs.current;
      return () => {
      Object.values(timers).forEach(clearInterval);
    };
  }, []);

  const updateExportState = useCallback((format: ExportFormat, updates: Partial<ExportState>) => {
    setExportStates(prev => ({
      ...prev,
      [format]: { ...prev[format], ...updates }
    }));
  }, []);

  const pollExportStatus = useCallback(async (taskId: string, format: ExportFormat) => {
    try {
      const status = await getExportStatus(taskId);
      
      updateExportState(format, {
        status: status.status,
        progress: status.progress,
      });

      if (status.status === 'completed') {
        // 停止轮询
        if (pollingRefs.current[taskId]) {
          clearInterval(pollingRefs.current[taskId]);
          delete pollingRefs.current[taskId];
        }
        
        // 自动下载
        const blob = await downloadExport(taskId);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `presentation.${format === 'png' || format === 'jpg' ? 'zip' : format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        updateExportState(format, { fileName: a.download });
        
        // 3秒后重置状态
        setTimeout(() => {
          updateExportState(format, { status: 'idle', progress: 0, taskId: undefined });
        }, 3000);
        
      } else if (status.status === 'failed') {
        if (pollingRefs.current[taskId]) {
          clearInterval(pollingRefs.current[taskId]);
          delete pollingRefs.current[taskId];
        }
        updateExportState(format, { 
          status: 'failed', 
          error: status.errorMessage || '导出失败' 
        });
      }
    } catch (error) {
      console.error('轮询状态失败:', error);
    }
  }, [updateExportState]);

  const handleExport = async (format: ExportFormat) => {
    // 重置该格式的状态
    updateExportState(format, { status: 'pending', progress: 0, error: undefined });
    
    try {
      let response;
      
      switch (format) {
        case 'pptx':
          response = await exportPptx({ 
            presentationId, 
            quality: 'high',
            slideRange: 'all',
            includeNotes: false 
          });
          break;
        case 'pdf':
          response = await exportPdf({ 
            presentationId, 
            quality: 'high',
            slideRange: 'all',
            includeNotes: false 
          });
          break;
        case 'png':
        case 'jpg':
          response = await exportImages({ 
            presentationId, 
            format,
            quality: 'high',
            slideRange: 'all'
          });
          break;
      }

      updateExportState(format, { 
        status: 'processing', 
        taskId: response.taskId,
        progress: 10 
      });

      // 开始轮询状态
      pollingRefs.current[response.taskId] = setInterval(
        () => pollExportStatus(response.taskId, format),
        POLLING_INTERVAL
      );
      
    } catch (error) {
      updateExportState(format, { 
        status: 'failed', 
        error: error instanceof Error ? error.message : '导出失败' 
      });
    }
  };

  const getFormatIcon = (format: ExportFormat) => {
    switch (format) {
      case 'pptx':
        return <FileText className="w-5 h-5 text-orange-500" />;
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-500" />;
      case 'png':
      case 'jpg':
        return <ImageIcon className="w-5 h-5 text-green-500" />;
    }
  };

  const getFormatLabel = (format: ExportFormat) => {
    switch (format) {
      case 'pptx':
        return '导出 PPTX';
      case 'pdf':
        return '导出 PDF';
      case 'png':
        return '导出 PNG 图片';
      case 'jpg':
        return '导出 JPG 图片';
    }
  };

  const getFormatDescription = (format: ExportFormat) => {
    switch (format) {
      case 'pptx':
        return 'PowerPoint 格式，可编辑';
      case 'pdf':
        return 'PDF 文档，适合分享';
      case 'png':
      case 'jpg':
        return '每页一张图片，打包下载';
    }
  };

  const isExporting = Object.values(exportStates).some(
    state => state.status === 'pending' || state.status === 'processing'
  );

  return (
    <div className="relative">
      {/* 主按钮 */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        whileHover={{ scale: isExporting ? 1 : 1.02 }}
        whileTap={{ scale: isExporting ? 1 : 0.98 }}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium
          transition-all duration-200
          ${isExporting 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
            : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 shadow-md hover:shadow-lg'
          }
        `}
      >
        {isExporting ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>导出中...</span>
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            <span>导出</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </>
        )}
      </motion.button>

      {/* 下拉菜单 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
          >
            <div className="p-2">
              <div className="flex items-center justify-between px-3 py-2 border-b border-gray-100">
                <span className="text-sm font-medium text-gray-700">选择导出格式</span>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="py-2 space-y-1">
                {(['pptx', 'pdf', 'png', 'jpg'] as ExportFormat[]).map((format) => {
                  const state = exportStates[format];
                  const isProcessing = state.status === 'pending' || state.status === 'processing';
                  
                  return (
                    <motion.button
                      key={format}
                      onClick={() => handleExport(format)}
                      disabled={isProcessing || state.status === 'completed'}
                      whileHover={{ scale: isProcessing ? 1 : 1.01 }}
                      whileTap={{ scale: isProcessing ? 1 : 0.99 }}
                      className={`
                        w-full flex items-center gap-3 px-3 py-3 rounded-lg
                        transition-colors text-left
                        ${state.status === 'completed' 
                          ? 'bg-green-50 border border-green-100' 
                          : state.status === 'failed'
                          ? 'bg-red-50 border border-red-100'
                          : isProcessing
                          ? 'bg-gray-50 cursor-default'
                          : 'hover:bg-gray-50'
                        }
                      `}
                    >
                      <div className={`
                        w-10 h-10 rounded-lg flex items-center justify-center
                        ${state.status === 'completed' 
                          ? 'bg-green-100' 
                          : state.status === 'failed'
                          ? 'bg-red-100'
                          : 'bg-gray-100'
                        }
                      `}>
                        {state.status === 'completed' ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : state.status === 'failed' ? (
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        ) : isProcessing ? (
                          <Loader2 className="w-5 h-5 text-gray-500 animate-spin" />
                        ) : (
                          getFormatIcon(format)
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`
                            text-sm font-medium
                            ${state.status === 'completed' 
                              ? 'text-green-700' 
                              : state.status === 'failed'
                              ? 'text-red-700'
                              : 'text-gray-700'
                            }
                          `}>
                            {getFormatLabel(format)}
                          </span>
                          {isProcessing && (
                            <span className="text-xs text-gray-500">
                              {state.progress}%
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 truncate">
                          {state.error || getFormatDescription(format)}
                        </p>
                        
                        {/* 进度条 */}
                        {isProcessing && (
                          <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                            <motion.div 
                              className="h-full bg-blue-500 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${state.progress}%` }}
                              transition={{ duration: 0.3 }}
                            />
                          </div>
                        )}
                      </div>
                    </motion.button>
                  );
                })}
              </div>
              
              <div className="px-3 py-2 border-t border-gray-100">
                <p className="text-xs text-gray-400">
                  导出完成后将自动下载文件
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
