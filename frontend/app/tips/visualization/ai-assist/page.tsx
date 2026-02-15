// app/tips/visualization/ai-assist/page.tsx
// AI 智能选图页面 - 上传数据后由 AI 推荐合适的图表类型

'use client';

import {useState, useCallback, Suspense} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
  ArrowLeft,
  Sparkles,
  Upload,
  Brain,
  CheckCircle,
  Loader2
} from 'lucide-react';
import type {ParsedData, ChartType} from '@/types/visualization';
import FileUploader from '@/components/visualization/DataSourceSelector/FileUploader';
import AIRecommend, {type RecommendedChart} from '@/components/visualization/AIRecommend';

/**
 * 步骤枚举
 */
type Step = 'upload' | 'analyzing' | 'result';

/**
 * AI 辅助页面内容组件
 * 使用 useSearchParams 需要包裹在 Suspense 中
 */
function AIAssistPageContent() {
  const router = useRouter();

  // 当前步骤
  const [currentStep, setCurrentStep] = useState<Step>('upload');
  // 解析后的数据
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  // 选中的推荐图表
  const [selectedChart, setSelectedChart] = useState<RecommendedChart | null>(null);

  /**
     * 处理文件上传成功
     * @param data - 解析后的数据
     */
  const handleFileUpload = useCallback((data: ParsedData) => {
    // 保存解析后的数据
    setParsedData(data);
    // 进入分析步骤
    setCurrentStep('analyzing');

    // 模拟 AI 分析延迟后进入结果步骤
    // 实际分析在 AIRecommend 组件内部进行
    setTimeout(() => {
      setCurrentStep('result');
    }, 2000);
  }, []);

  /**
     * 处理推荐图表选择
     * @param chart - 选中的推荐图表
     */
  const handleChartSelect = useCallback((chart: RecommendedChart) => {
    setSelectedChart(chart);

    // 跳转到图表创建页，传递图表类型参数
    router.push(`/tips/visualization/create?type=${chart.chartType}`);
  }, [router]);

  /**
     * 处理重新上传
     */
  const handleReupload = () => {
    setParsedData(null);
    setSelectedChart(null);
    setCurrentStep('upload');
  };

  /**
     * 处理返回按钮点击
     */
  const handleBack = () => {
    router.push('/tips/visualization');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-indigo-50/50">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/4 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl" />
      </div>

      {/* 导航栏 */}
      <motion.nav
        initial={{opacity: 0, y: -20}}
        animate={{opacity: 1, y: 0}}
        transition={{duration: 0.1}}
        className="relative z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center">
            {/* 返回按钮 */}
            <button
              onClick={handleBack}
              className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors group"
            >
              <div className="p-2 rounded-lg group-hover:bg-gray-100 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </div>
              <span className="font-medium">返回</span>
            </button>

            {/* 标题 */}
            <div className="ml-6 flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-gray-900">AI 智能选图</h1>
                <p className="text-xs text-gray-500">上传数据，AI 为你推荐最佳图表</p>
              </div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* 步骤指示器 */}
      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-center gap-4">
          {/* 步骤 1：上传数据 */}
          <motion.div
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.1, delay: 0.1}}
            className="flex items-center gap-2"
          >
            <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center
                            ${currentStep === 'upload'
      ? 'bg-purple-500 text-white'
      : currentStep === 'analyzing' || currentStep === 'result'
        ? 'bg-green-500 text-white'
        : 'bg-gray-200 text-gray-500'
    }
                        `}>
              {currentStep === 'analyzing' || currentStep === 'result' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <span className="text-sm font-medium">1</span>
              )}
            </div>
            <span className={`
                            text-sm font-medium
                            ${currentStep === 'upload' ? 'text-purple-600' : 'text-gray-500'}
                        `}>
                            上传数据
            </span>
          </motion.div>

          {/* 连接线 */}
          <div className={`
                        w-12 h-0.5
                        ${currentStep === 'analyzing' || currentStep === 'result'
      ? 'bg-green-500'
      : 'bg-gray-200'
    }
                    `} />

          {/* 步骤 2：AI 分析 */}
          <motion.div
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.1, delay: 0.2}}
            className="flex items-center gap-2"
          >
            <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center
                            ${currentStep === 'analyzing'
      ? 'bg-purple-500 text-white'
      : currentStep === 'result'
        ? 'bg-green-500 text-white'
        : 'bg-gray-200 text-gray-500'
    }
                        `}>
              {currentStep === 'result' ? (
                <CheckCircle className="w-5 h-5" />
              ) : currentStep === 'analyzing' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <span className="text-sm font-medium">2</span>
              )}
            </div>
            <span className={`
                            text-sm font-medium
                            ${currentStep === 'analyzing' ? 'text-purple-600' : 'text-gray-500'}
                        `}>
                            AI 分析
            </span>
          </motion.div>

          {/* 连接线 */}
          <div className={`
                        w-12 h-0.5
                        ${currentStep === 'result' ? 'bg-green-500' : 'bg-gray-200'}
                    `} />

          {/* 步骤 3：推荐结果 */}
          <motion.div
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.1, delay: 0.3}}
            className="flex items-center gap-2"
          >
            <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center
                            ${currentStep === 'result'
      ? 'bg-purple-500 text-white'
      : 'bg-gray-200 text-gray-500'
    }
                        `}>
              <span className="text-sm font-medium">3</span>
            </div>
            <span className={`
                            text-sm font-medium
                            ${currentStep === 'result' ? 'text-purple-600' : 'text-gray-500'}
                        `}>
                            推荐结果
            </span>
          </motion.div>
        </div>
      </div>

      {/* 主内容区域 */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <AnimatePresence mode="wait">
          {/* 步骤 1：上传数据 */}
          {currentStep === 'upload' && (
            <motion.div
              key="upload"
              initial={{opacity: 0, y: 20}}
              animate={{opacity: 1, y: 0}}
              exit={{opacity: 0, y: -20}}
              transition={{duration: 0.1}}
              className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm p-8"
            >
              {/* 区域标题 */}
              <div className="text-center mb-6">
                <div className="w-16 h-16 mx-auto rounded-full bg-purple-100 flex items-center justify-center mb-4">
                  <Upload className="w-8 h-8 text-purple-500" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                                    上传你的数据文件
                </h2>
                <p className="text-sm text-gray-500">
                                    AI 将分析数据特征，为你推荐最合适的图表类型
                </p>
              </div>

              {/* 文件上传组件 */}
              <FileUploader onUpload={handleFileUpload} />
            </motion.div>
          )}

          {/* 步骤 2：AI 分析中 */}
          {currentStep === 'analyzing' && (
            <motion.div
              key="analyzing"
              initial={{opacity: 0, y: 20}}
              animate={{opacity: 1, y: 0}}
              exit={{opacity: 0, y: -20}}
              transition={{duration: 0.1}}
              className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm p-12"
            >
              {/* 加载动画 */}
              <div className="flex flex-col items-center text-center">
                {/* 动画圆环 */}
                <div className="relative mb-6">
                  <div className="w-24 h-24 rounded-full border-4 border-gray-200" />
                  <div className="absolute inset-0 w-24 h-24 rounded-full border-4 border-transparent border-t-purple-500 animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Sparkles className="w-10 h-10 text-purple-500" />
                  </div>
                </div>

                {/* 加载文字 */}
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                                    AI 正在分析你的数据
                </h2>
                <p className="text-sm text-gray-500 mb-4">
                                    识别数据特征，匹配最佳图表类型...
                </p>

                {/* 数据信息 */}
                {parsedData && (
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span>{parsedData.totalRows} 行数据</span>
                    <span>{parsedData.fields.length} 个字段</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* 步骤 3：推荐结果 */}
          {currentStep === 'result' && parsedData && (
            <motion.div
              key="result"
              initial={{opacity: 0, y: 20}}
              animate={{opacity: 1, y: 0}}
              exit={{opacity: 0, y: -20}}
              transition={{duration: 0.1}}
              className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm overflow-hidden"
            >
              {/* AI 推荐组件 */}
              <AIRecommend
                data={parsedData}
                onSelect={handleChartSelect}
              />

              {/* 重新上传按钮 */}
              <div className="p-4 border-t border-gray-200/50 bg-gray-50/50">
                <button
                  onClick={handleReupload}
                  className="
                                        w-full py-2 text-sm text-gray-600
                                        hover:text-gray-900 transition-colors
                                    "
                >
                                    重新上传数据
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

/**
 * AI 辅助页面组件
 * 包含 Suspense 边界以支持 useSearchParams
 */
export default function AIAssistPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-indigo-50/50">
        <div className="text-gray-400">加载中...</div>
      </div>
    }>
      <AIAssistPageContent />
    </Suspense>
  );
}
