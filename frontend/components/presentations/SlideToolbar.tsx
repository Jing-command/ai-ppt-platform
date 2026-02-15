'use client';

import {motion} from 'framer-motion';
import {
  Undo2,
  Redo2,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  Save
} from 'lucide-react';

interface SlideToolbarProps {
  currentSlideIndex: number;
  totalSlides: number;
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onAddSlide: () => void;
  onDeleteSlide: () => void;
  onPrevSlide: () => void;
  onNextSlide: () => void;
  onSave: () => void;
  onExport: () => void;
  onPreview: () => void;
  saving?: boolean;
}

export default function SlideToolbar({
  currentSlideIndex,
  totalSlides,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  onAddSlide,
  onDeleteSlide,
  onPrevSlide,
  onNextSlide,
  onSave,
  onExport,
  onPreview,
  saving = false
}: SlideToolbarProps) {
  return (
    <div className="bg-white border-t border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between max-w-[1600px] mx-auto">
        {/* 左侧：撤销重做 */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={onUndo}
            disabled={!canUndo}
            whileHover={canUndo ? {scale: 1.05} : {}}
            whileTap={canUndo ? {scale: 0.95} : {}}
            className={`
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              ${canUndo
      ? 'text-gray-700 hover:bg-gray-100'
      : 'text-gray-300 cursor-not-allowed'
    }
            `}
            title="撤销 (Ctrl+Z)"
          >
            <Undo2 className="w-4 h-4" />
            <span className="hidden sm:inline">撤销</span>
          </motion.button>

          <motion.button
            onClick={onRedo}
            disabled={!canRedo}
            whileHover={canRedo ? {scale: 1.05} : {}}
            whileTap={canRedo ? {scale: 0.95} : {}}
            className={`
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              ${canRedo
      ? 'text-gray-700 hover:bg-gray-100'
      : 'text-gray-300 cursor-not-allowed'
    }
            `}
            title="重做 (Ctrl+Y)"
          >
            <Redo2 className="w-4 h-4" />
            <span className="hidden sm:inline">重做</span>
          </motion.button>

          <div className="w-px h-6 bg-gray-200 mx-2" />

          <motion.button
            onClick={onAddSlide}
            whileHover={{scale: 1.05}}
            whileTap={{scale: 0.95}}
            className="
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              text-blue-600 hover:bg-blue-50
            "
            title="添加幻灯片"
          >
            <Plus className="w-4 h-4" />
            <span>添加页面</span>
          </motion.button>

          <motion.button
            onClick={onDeleteSlide}
            disabled={totalSlides <= 1}
            whileHover={totalSlides > 1 ? {scale: 1.05} : {}}
            whileTap={totalSlides > 1 ? {scale: 0.95} : {}}
            className={`
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              ${totalSlides > 1
      ? 'text-red-600 hover:bg-red-50'
      : 'text-gray-300 cursor-not-allowed'
    }
            `}
            title="删除当前幻灯片"
          >
            <Trash2 className="w-4 h-4" />
            <span className="hidden sm:inline">删除</span>
          </motion.button>
        </div>

        {/* 中间：幻灯片导航 */}
        <div className="flex items-center gap-3">
          <motion.button
            onClick={onPrevSlide}
            disabled={currentSlideIndex === 0}
            whileHover={currentSlideIndex > 0 ? {scale: 1.05} : {}}
            whileTap={currentSlideIndex > 0 ? {scale: 0.95} : {}}
            className={`
              p-2 rounded-lg
              ${currentSlideIndex > 0
      ? 'text-gray-700 hover:bg-gray-100'
      : 'text-gray-300 cursor-not-allowed'
    }
            `}
          >
            <ChevronLeft className="w-5 h-5" />
          </motion.button>

          <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 rounded-lg">
            <span className="text-sm font-medium text-gray-700">
              {currentSlideIndex + 1}
            </span>
            <span className="text-sm text-gray-400">/</span>
            <span className="text-sm text-gray-500">
              {totalSlides}
            </span>
          </div>

          <motion.button
            onClick={onNextSlide}
            disabled={currentSlideIndex >= totalSlides - 1}
            whileHover={currentSlideIndex < totalSlides - 1 ? {scale: 1.05} : {}}
            whileTap={currentSlideIndex < totalSlides - 1 ? {scale: 0.95} : {}}
            className={`
              p-2 rounded-lg
              ${currentSlideIndex < totalSlides - 1
      ? 'text-gray-700 hover:bg-gray-100'
      : 'text-gray-300 cursor-not-allowed'
    }
            `}
          >
            <ChevronRight className="w-5 h-5" />
          </motion.button>
        </div>

        {/* 右侧：保存和导出 */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={onPreview}
            whileHover={{scale: 1.02}}
            whileTap={{scale: 0.98}}
            className="
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              text-gray-700 hover:bg-gray-100
            "
          >
            <Eye className="w-4 h-4" />
            <span className="hidden sm:inline">预览</span>
          </motion.button>

          <motion.button
            onClick={onExport}
            whileHover={{scale: 1.02}}
            whileTap={{scale: 0.98}}
            className="
              flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
              text-gray-700 hover:bg-gray-100
            "
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">导出</span>
          </motion.button>

          <div className="w-px h-6 bg-gray-200 mx-2" />

          <motion.button
            onClick={onSave}
            disabled={saving}
            whileHover={{scale: 1.02}}
            whileTap={{scale: 0.98}}
            className="
              flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
              text-white bg-gradient-to-r from-blue-600 to-blue-500
              hover:from-blue-700 hover:to-blue-600
              shadow-md hover:shadow-lg
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-shadow duration-200
            "
          >
            <Save className={`w-4 h-4 ${saving ? 'animate-pulse' : ''}`} />
            <span>{saving ? '保存中...' : '保存'}</span>
          </motion.button>
        </div>
      </div>
    </div>
  );
}
