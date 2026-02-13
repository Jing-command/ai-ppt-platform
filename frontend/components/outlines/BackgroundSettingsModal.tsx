'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Wand2, Upload, Palette, Check, Loader2 } from 'lucide-react';
import { OutlineBackground, BackgroundType } from '@/types/outline';

interface BackgroundSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  background?: OutlineBackground;
  onSave: (background: OutlineBackground) => void;
}

const PRESET_COLORS = [
  '#ffffff', '#f8fafc', '#f1f5f9', '#e2e8f0',  // 灰白
  '#fef2f2', '#fee2e2', '#fecaca',              // 红色系
  '#fff7ed', '#ffedd5', '#fed7aa',              // 橙色系
  '#fefce8', '#fef9c3', '#fde047',              // 黄色系
  '#f0fdf4', '#dcfce7', '#bbf7d0',              // 绿色系
  '#eff6ff', '#dbeafe', '#bfdbfe',              // 蓝色系
  '#faf5ff', '#f3e8ff', '#e9d5ff',              // 紫色系
  '#1e293b', '#334155', '#475569',              // 深色
];

export default function BackgroundSettingsModal({
  isOpen,
  onClose,
  background,
  onSave,
}: BackgroundSettingsModalProps) {
  const [activeTab, setActiveTab] = useState<BackgroundType>(background?.type || 'ai');
  const [aiPrompt, setAiPrompt] = useState(background?.prompt || '');
  const [solidColor, setSolidColor] = useState(background?.color || '#ffffff');
  const [uploadedImage, setUploadedImage] = useState<string | null>(background?.url || null);
  const [uploading, setUploading] = useState(false);
  const [opacity, setOpacity] = useState(background?.opacity ?? 1);
  const [blur, setBlur] = useState(background?.blur ?? 0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      alert('请上传图片文件');
      return;
    }

    // 验证文件大小 (最大 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过 5MB');
      return;
    }

    setUploading(true);

    try {
      // 模拟上传 - 实际项目中应该调用上传API
      // const formData = new FormData();
      // formData.append('file', file);
      // const response = await uploadFile(formData);
      // setUploadedImage(response.url);

      // 临时使用本地预览
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target?.result as string);
        setUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      alert('上传失败，请重试');
      setUploading(false);
    }
  };

  const handleSave = () => {
    let newBackground: OutlineBackground;

    switch (activeTab) {
      case 'ai':
        newBackground = {
          type: 'ai',
          prompt: aiPrompt.trim() || undefined,
          opacity,
          blur,
        };
        break;
      case 'upload':
        if (!uploadedImage) {
          alert('请先上传图片');
          return;
        }
        newBackground = {
          type: 'upload',
          url: uploadedImage,
          opacity,
          blur,
        };
        break;
      case 'solid':
        newBackground = {
          type: 'solid',
          color: solidColor,
          opacity,
        };
        break;
      default:
        newBackground = { type: 'solid', color: '#ffffff' };
    }

    onSave(newBackground);
    onClose();
  };

  const tabs = [
    { id: 'ai' as BackgroundType, label: 'AI生成', icon: Wand2 },
    { id: 'upload' as BackgroundType, label: '上传图片', icon: Upload },
    { id: 'solid' as BackgroundType, label: '纯色', icon: Palette },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* 弹窗 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
          >
            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
              {/* 头部 */}
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-xl font-semibold text-[var(--color-text)]">
                  背景设置
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* 标签页 */}
              <div className="flex border-b border-gray-100">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex-1 flex items-center justify-center gap-2 py-4 px-6
                      font-medium text-sm transition-colors
                      ${activeTab === tab.id
                        ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                      }
                    `}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* 内容区 */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {/* AI生成 */}
                {activeTab === 'ai' && (
                  <div className="space-y-4">
                    <div>
                      <label className="label-text mb-2 block">
                        背景描述
                        <span className="text-gray-400 font-normal ml-1">（AI将据此生成背景图）</span>
                      </label>
                      <textarea
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                        placeholder="例如：淡蓝色渐变背景，带有科技感的光效线条，简洁商务风格..."
                        rows={4}
                        className="input-field resize-none"
                      />
                    </div>

                    <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
                      <p className="flex items-start gap-2">
                        <Wand2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        <span>
                          AI将根据您的描述生成独特的PPT背景。建议描述颜色、风格和元素。
                          <br />
                          生成需要1-2分钟，将在创建PPT时自动处理。
                        </span>
                      </p>
                    </div>
                  </div>
                )}

                {/* 上传图片 */}
                {activeTab === 'upload' && (
                  <div className="space-y-4">
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className={`
                        border-2 border-dashed rounded-xl p-8
                        flex flex-col items-center justify-center
                        cursor-pointer transition-colors
                        ${uploadedImage
                          ? 'border-green-400 bg-green-50'
                          : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50/30'
                        }
                      `}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="hidden"
                      />

                      {uploading ? (
                        <>
                          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                          <p className="text-gray-500">上传中...</p>
                        </>
                      ) : uploadedImage ? (
                        <>
                          <div className="relative w-full max-w-xs">
                            <Image
                              src={uploadedImage} width={320} height={192}
                              alt="预览"
                              className="w-full h-48 object-cover rounded-lg"
                            />
                            <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                              <span className="text-white font-medium">点击更换图片</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 mt-4 text-green-600">
                            <Check className="w-5 h-5" />
                            <span>图片已上传</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                            <Upload className="w-8 h-8 text-blue-600" />
                          </div>
                          <p className="text-gray-600 font-medium mb-2">点击上传图片</p>
                          <p className="text-gray-400 text-sm">支持 JPG、PNG 格式，最大 5MB</p>
                        </>
                      )}
                    </div>

                    {uploadedImage && (
                      <button
                        onClick={() => setUploadedImage(null)}
                        className="text-red-500 text-sm hover:underline"
                      >
                        移除图片
                      </button>
                    )}
                  </div>
                )}

                {/* 纯色 */}
                {activeTab === 'solid' && (
                  <div className="space-y-6">
                    <div>
                      <label className="label-text mb-3 block">选择颜色</label>
                      <div className="grid grid-cols-8 gap-3">
                        {PRESET_COLORS.map((color) => (
                          <button
                            key={color}
                            onClick={() => setSolidColor(color)}
                            className={`
                              w-10 h-10 rounded-lg border-2 transition-all
                              ${solidColor === color
                                ? 'border-blue-500 scale-110 shadow-md'
                                : 'border-gray-200 hover:border-gray-300'
                              }
                            `}
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="label-text mb-2 block">自定义颜色</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="color"
                          value={solidColor}
                          onChange={(e) => setSolidColor(e.target.value)}
                          className="w-12 h-12 rounded-lg cursor-pointer border border-gray-200"
                        />
                        <input
                          type="text"
                          value={solidColor}
                          onChange={(e) => setSolidColor(e.target.value)}
                          className="input-field flex-1"
                          placeholder="#ffffff"
                        />
                      </div>
                    </div>

                    {/* 预览 */}
                    <div>
                      <label className="label-text mb-2 block">预览</label>
                      <div
                        className="h-32 rounded-lg border border-gray-200 flex items-center justify-center"
                        style={{ backgroundColor: solidColor }}
                      >
                        <span className="text-gray-400 text-sm">背景预览</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 通用设置 */}
                {(activeTab === 'ai' || activeTab === 'upload') && (
                  <div className="mt-6 pt-6 border-t border-gray-100 space-y-4">
                    <h4 className="font-medium text-gray-700">效果设置</h4>

                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm text-gray-600">透明度</label>
                        <span className="text-sm text-gray-400">{Math.round(opacity * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min={0.1}
                        max={1}
                        step={0.1}
                        value={opacity}
                        onChange={(e) => setOpacity(parseFloat(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm text-gray-600">模糊度</label>
                        <span className="text-sm text-gray-400">{blur}px</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={20}
                        step={1}
                        value={blur}
                        onChange={(e) => setBlur(parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      />
                      <p className="text-xs text-gray-400 mt-1">适当模糊可避免背景干扰文字阅读</p>
                    </div>
                  </div>
                )}
              </div>

              {/* 底部按钮 */}
              <div className="flex justify-end gap-3 p-6 border-t border-gray-100 bg-gray-50">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleSave}
                  className="
                    px-4 py-2 bg-blue-600 text-white rounded-lg
                    hover:bg-blue-700 transition-colors
                    flex items-center gap-2
                  "
                >
                  <Check className="w-4 h-4" />
                  保存设置
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
