'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';

// 提示数据配置 - 极简单行文字
const tips = [
  '在提示词中加入"简洁"关键词，可以让生成的大纲更加精炼',
  '上传 Excel 数据后，AI 会自动分析并推荐最合适的图表类型',
  '点击"重新生成"按钮，AI 会根据相同主题生成不同风格的版本',
  '使用 Ctrl + Enter 快捷键可以快速触发生成，无需点击按钮',
  '选择热门模板后，AI 会根据模板风格自动调整内容的语气和结构'
];

/**
 * DashboardTips 组件 - 科技感发光提示条
 * 
 * 设计理念：
 * - 渐变流光边框：边框颜色流动动画，营造科技感
 * - 玻璃拟态背景：半透明 + 模糊，现代感十足
 * - 发光效果：微妙的光晕，吸引目光但不刺眼
 * - 扫光动画：光斑从左到右扫过，增加动态感
 * - 进度指示：右侧细线进度条 + 数字，更科技感
 */
export function DashboardTips() {
  // 当前提示索引
  const [currentIndex, setCurrentIndex] = useState(0);
  // 是否暂停自动轮播
  const [isPaused, setIsPaused] = useState(false);

  // 切换到下一条提示
  const handleNext = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % tips.length);
  }, []);

  // 切换到上一条提示
  const handlePrev = useCallback(() => {
    setCurrentIndex((prev) => (prev - 1 + tips.length) % tips.length);
  }, []);

  // 自动轮播定时器 - 5秒切换一次
  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(handleNext, 5000);
    return () => clearInterval(timer);
  }, [isPaused, handleNext]);

  return (
    <motion.div
      // 入场动画：淡入 + 轻微上移
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.4, ease: 'easeOut' }}
      className="mt-4"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* 主容器 - 科技感发光设计 */}
      <div className="group relative">
        
        {/* 渐变流光边框层 - 使用伪元素实现圆角渐变边框 */}
        <div 
          className="absolute -inset-[1px] rounded-xl opacity-50 group-hover:opacity-70 transition-opacity duration-300"
          style={{
            // 渐变背景作为边框 - 淡雅灰蓝色
            background: 'linear-gradient(90deg, #94a3b8, #a5b4fc, #c4b5fd, #cbd5e1, #94a3b8)',
            backgroundSize: '200% 100%',
            animation: 'borderFlow 3s linear infinite',
          }}
        />
        
        {/* 内部内容层 - 玻璃拟态背景 */}
        <div 
          className="relative flex items-center h-10 px-4 rounded-xl overflow-hidden"
          style={{
            // 玻璃拟态背景 - 浅色半透明
            background: 'rgba(255, 255, 255, 0.85)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
          }}
        >
          {/* 扫光效果层 - 光斑从左到右扫过 */}
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 4s ease-in-out infinite',
            }}
          />
          
          {/* 微妙发光效果 - 内阴影模拟 */}
          <div 
            className="absolute inset-0 pointer-events-none rounded-xl"
            style={{
              boxShadow: 'inset 0 1px 0 0 rgba(255,255,255,0.1), inset 0 -1px 0 0 rgba(0,0,0,0.2)',
            }}
          />

          {/* 左侧：AI 图标 + 发光效果 */}
          <div className="flex items-center gap-2 mr-3 flex-shrink-0">
            <div className="relative">
              {/* 图标发光背景 */}
              <div 
                className="absolute inset-0 blur-sm rounded-full"
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                  opacity: 0.5,
                }}
              />
              <Sparkles className="relative w-4 h-4 text-violet-500" />
            </div>
            {/* 提示标签 */}
            <span className="text-[11px] font-medium text-violet-500/80 uppercase tracking-wider">
              TIP
            </span>
          </div>

          {/* 中间：提示文字 - 单行截断 */}
          <AnimatePresence mode="wait">
            <motion.p
              key={currentIndex}
              // 文字切换动画：淡入 + 轻微位移
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="flex-1 text-[13px] text-gray-600 truncate"
            >
              {tips[currentIndex]}
            </motion.p>
          </AnimatePresence>

          {/* 右侧：进度指示器 + 切换按钮 */}
          <div className="flex items-center gap-3 ml-4 flex-shrink-0">
            {/* 进度指示器 - 细线进度条 + 数字 */}
            <div className="flex items-center gap-2">
              {/* 进度数字 */}
              <span className="text-[11px] font-mono text-gray-400">
                {String(currentIndex + 1).padStart(2, '0')}/{String(tips.length).padStart(2, '0')}
              </span>
              {/* 细线进度条 */}
              <div className="w-12 h-0.5 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{
                    background: 'linear-gradient(90deg, #a5b4fc, #c4b5fd)',
                  }}
                  initial={{ width: '0%' }}
                  animate={{ width: isPaused ? '0%' : '100%' }}
                  transition={{ 
                    duration: 5, 
                    ease: 'linear',
                    repeat: Infinity,
                    repeatType: 'restart'
                  }}
                />
              </div>
            </div>

            {/* 切换按钮 - 悬停显示 */}
            <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <button
                onClick={handlePrev}
                // 按钮悬停发光效果
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-all duration-200"
                aria-label="上一条提示"
              >
                <ChevronLeft className="w-3.5 h-3.5 text-gray-400 hover:text-violet-500 transition-colors" />
              </button>
              <button
                onClick={handleNext}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-all duration-200"
                aria-label="下一条提示"
              >
                <ChevronRight className="w-3.5 h-3.5 text-gray-400 hover:text-violet-500 transition-colors" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* CSS 动画关键帧 - 注入到组件中 */}
      <style jsx global>{`
        /* 边框流光动画 - 渐变色从左到右流动 */
        @keyframes borderFlow {
          0% {
            background-position: 0% 50%;
          }
          100% {
            background-position: 200% 50%;
          }
        }
        
        /* 扫光动画 - 光斑从左到右扫过 */
        @keyframes shimmer {
          0%, 100% {
            background-position: -200% 0;
          }
          50% {
            background-position: 200% 0;
          }
        }
        
        /* 尊重用户的减少动画偏好设置 */
        @media (prefers-reduced-motion: reduce) {
          @keyframes borderFlow {
            0%, 100% {
              background-position: 0% 50%;
            }
          }
          @keyframes shimmer {
            0%, 100% {
              background-position: -200% 0;
            }
          }
        }
      `}</style>
    </motion.div>
  );
}
