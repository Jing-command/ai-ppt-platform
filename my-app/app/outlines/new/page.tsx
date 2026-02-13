'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles, Loader2 } from 'lucide-react';
import { generateOutline } from '@/lib/api/outlines';
import { AxiosError } from 'axios';

export default function GenerateOutlinePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [numSlides, setNumSlides] = useState(15);
  const [language, setLanguage] = useState<'zh' | 'en'>('zh');
  const [style, setStyle] = useState<'business' | 'education' | 'creative' | 'technical'>('business');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (prompt.trim().length < 10) {
      setError('请输入至少 10 个字符的描述');
      return;
    }

    setLoading(true);

    try {
      const response = await generateOutline({
        prompt: prompt.trim(),
        numSlides,
        language,
        style,
      });

      alert(`生成任务已提交！\n任务 ID: ${response.taskId}\n预计时间: ${response.estimatedTime} 秒`);
      router.push('/outlines');
    } catch (err) {
      const axiosError = err as AxiosError;
      if (axiosError.response?.status === 401) {
        router.push('/login');
      } else {
        setError((axiosError.response?.data as { message?: string })?.message || '生成失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b border-[var(--color-border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center">
            <button
              onClick={() => router.push('/outlines')}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>返回大纲列表</span>
            </button>
          </div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl border border-[var(--color-border)] shadow-sm"
        >
          {/* 头部 */}
          <div className="p-6 border-b border-[var(--color-border)]">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Sparkles className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-[var(--color-text)]">AI 生成大纲</h1>
                <p className="text-sm text-[var(--color-text-muted)]">
                  输入主题和页数，AI 将为你规划每一页的内容
                </p>
              </div>
            </div>
          </div>

          {/* 表单 */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* 错误提示 */}
            {error && (
              <div className="alert-error">{error}</div>
            )}

            {/* 主题描述 */}
            <div className="space-y-2">
              <label htmlFor="prompt" className="label-text">
                PPT 主题描述
                <span className="text-red-500">*</span>
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="例如：制作一个关于人工智能在医疗领域应用的PPT，介绍AI技术在诊断、治疗、药物研发等方面的应用案例..."
                rows={4}
                className="input-field resize-none"
                disabled={loading}
              />
              <p className="text-xs text-[var(--color-text-muted)]">
                描述越详细，AI 生成的内容越精准
              </p>
            </div>

            {/* 页数设置 */}
            <div className="space-y-4">
              <label className="label-text">PPT 总页数: {numSlides} 页</label>
              <input
                type="range"
                min={3}
                max={50}
                value={numSlides}
                onChange={(e) => setNumSlides(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                disabled={loading}
              />
              <div className="flex justify-between text-xs text-[var(--color-text-muted)]">
                <span>3页</span>
                <span>建议 10-20 页</span>
                <span>50页</span>
              </div>
            </div>

            {/* 语言和风格 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="language" className="label-text">语言</label>
                <select
                  id="language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as 'zh' | 'en')}
                  className="input-field"
                  disabled={loading}
                >
                  <option value="zh">中文</option>
                  <option value="en">English</option>
                </select>
              </div>

              <div className="space-y-2">
                <label htmlFor="style" className="label-text">风格</label>
                <select
                  id="style"
                  value={style}
                  onChange={(e) => setStyle(e.target.value as typeof style)}
                  className="input-field"
                  disabled={loading}
                >
                  <option value="business">商务</option>
                  <option value="education">教育</option>
                  <option value="creative">创意</option>
                  <option value="technical">技术</option>
                </select>
              </div>
            </div>

            {/* 提交按钮 */}
            <div className="pt-4">
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className="
                  w-full py-3 px-4 rounded-lg
                  text-white font-medium
                  bg-gradient-to-r from-blue-600 to-blue-500
                  hover:from-blue-700 hover:to-blue-600
                  shadow-md hover:shadow-lg
                  transition-shadow duration-200
                  disabled:opacity-50 disabled:cursor-not-allowed
                  flex items-center justify-center gap-2
                "
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    AI 生成 {numSlides} 页大纲
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* 提示 */}
        <div className="mt-6 text-center text-sm text-[var(--color-text-muted)]">
          <p>💡 AI 将为每一页生成标题和内容建议</p>
        </div>
      </main>
    </div>
  );
}
