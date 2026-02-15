'use client';

import {useState, useEffect} from 'react';
import {motion} from 'framer-motion';
import {Plus, Trash2, GripVertical, Image as ImageIcon, Type, AlignLeft, List} from 'lucide-react';
import {Slide, SlideType, SlideContent} from '@/types/presentation';

interface SlideEditorProps {
  slide: Slide;
  onUpdate: (content: Partial<SlideContent>) => void;
  onTypeChange: (type: SlideType) => void;
}

const slideTypeOptions: { value: SlideType; label: string; icon: React.ReactNode; description: string }[] = [
    {
        value: 'title',
        label: '封面页',
        icon: <Type className="w-4 h-4" />,
        description: 'PPT 标题和副标题'
    },
    {
        value: 'content',
        label: '内容页',
        icon: <AlignLeft className="w-4 h-4" />,
        description: '文本和列表内容'
    },
    {
        value: 'section',
        label: '章节页',
        icon: <List className="w-4 h-4" />,
        description: '章节分隔页'
    },
    {
        value: 'chart',
        label: '图表页',
        icon: <ImageIcon className="w-4 h-4" />,
        description: '数据可视化'
    },
    {
        value: 'conclusion',
        label: '总结页',
        icon: <Type className="w-4 h-4" />,
        description: '总结和结论'
    }
];

export default function SlideEditor({slide, onUpdate, onTypeChange}: SlideEditorProps) {
    const {content, type} = slide;
    const [bullets, setBullets] = useState<string[]>(content.bullets || ['']);
    const [imagePrompt, setImagePrompt] = useState(slide.imagePrompt || '');

    /* eslint-disable react-hooks/exhaustive-deps */
    useEffect(() => {
        setBullets(content.bullets || ['']);
        setImagePrompt(slide.imagePrompt || '');
    }, [slide.id]);

    const handleBulletChange = (index: number, value: string) => {
        const newBullets = [...bullets];
        newBullets[index] = value;
        setBullets(newBullets);
        onUpdate({bullets: newBullets.filter(b => b.trim() !== '')});
    };

    const handleAddBullet = () => {
        setBullets([...bullets, '']);
    };

    const handleRemoveBullet = (index: number) => {
        const newBullets = bullets.filter((_, i) => i !== index);
        setBullets(newBullets.length > 0 ? newBullets : ['']);
        onUpdate({bullets: newBullets.filter(b => b.trim() !== '')});
    };

    const handleImagePromptChange = (value: string) => {
        setImagePrompt(value);
    // Note: imagePrompt is stored on the slide level, not in content
    // We need to handle this separately in the parent
    };

    const renderTitleEditor = () => (
        <div className="space-y-6">
            <div>
                <label className="label-text">主标题</label>
                <input
                    type="text"
                    value={content.title || ''}
                    onChange={(e) => onUpdate({title: e.target.value})}
                    className="input-field text-lg"
                    placeholder="输入 PPT 标题"
                />
            </div>

            <div>
                <label className="label-text">副标题</label>
                <input
                    type="text"
                    value={content.subtitle || ''}
                    onChange={(e) => onUpdate({subtitle: e.target.value})}
                    className="input-field"
                    placeholder="输入副标题（可选）"
                />
            </div>

            <div>
                <label className="label-text">演讲者/作者</label>
                <input
                    type="text"
                    value={content.author || ''}
                    onChange={(e) => onUpdate({author: e.target.value})}
                    className="input-field"
                    placeholder="输入演讲者或作者名称"
                />
            </div>
        </div>
    );

    const renderContentEditor = () => (
        <div className="space-y-6">
            <div>
                <label className="label-text">页面标题</label>
                <input
                    type="text"
                    value={content.title || ''}
                    onChange={(e) => onUpdate({title: e.target.value})}
                    className="input-field"
                    placeholder="输入页面标题"
                />
            </div>

            <div>
                <label className="label-text">正文内容</label>
                <textarea
                    value={content.text || ''}
                    onChange={(e) => onUpdate({text: e.target.value})}
                    className="input-field resize-none"
                    rows={6}
                    placeholder="输入正文内容..."
                />
            </div>

            <div>
                <label className="label-text flex items-center justify-between">
                    <span>要点列表</span>
                    <button
                        onClick={handleAddBullet}
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                        <Plus className="w-3 h-3" />
            添加
                    </button>
                </label>
                <div className="space-y-2">
                    {bullets.map((bullet, index) => (
                        <motion.div
                            key={index}
                            initial={{opacity: 0, x: -10}}
                            animate={{opacity: 1, x: 0}}
                            className="flex items-center gap-2"
                        >
                            <GripVertical className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <input
                                type="text"
                                value={bullet}
                                onChange={(e) => handleBulletChange(index, e.target.value)}
                                className="input-field flex-1 text-sm"
                                placeholder={`要点 ${index + 1}`}
                            />
                            <button
                                onClick={() => handleRemoveBullet(index)}
                                className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderSectionEditor = () => (
        <div className="space-y-6">
            <div>
                <label className="label-text">章节标题</label>
                <input
                    type="text"
                    value={content.title || ''}
                    onChange={(e) => onUpdate({title: e.target.value})}
                    className="input-field text-lg"
                    placeholder="输入章节标题"
                />
            </div>

            <div>
                <label className="label-text">章节描述</label>
                <textarea
                    value={content.description || ''}
                    onChange={(e) => onUpdate({description: e.target.value})}
                    className="input-field resize-none"
                    rows={4}
                    placeholder="输入章节描述（可选）"
                />
            </div>

            <div>
                <label className="label-text">章节编号</label>
                <input
                    type="text"
                    value={content.subtitle || ''}
                    onChange={(e) => onUpdate({subtitle: e.target.value})}
                    className="input-field w-24"
                    placeholder="如：第 1 章"
                />
            </div>
        </div>
    );

    const renderChartEditor = () => (
        <div className="space-y-6">
            <div>
                <label className="label-text">图表标题</label>
                <input
                    type="text"
                    value={content.title || ''}
                    onChange={(e) => onUpdate({title: e.target.value})}
                    className="input-field"
                    placeholder="输入图表标题"
                />
            </div>

            <div>
                <label className="label-text">图表说明</label>
                <textarea
                    value={content.description || ''}
                    onChange={(e) => onUpdate({description: e.target.value})}
                    className="input-field resize-none"
                    rows={3}
                    placeholder="输入图表说明文字"
                />
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">图表数据配置</p>
                <p className="text-xs text-gray-400">
          图表数据将在高级编辑器中配置，当前版本支持基础文本描述
                </p>
            </div>
        </div>
    );

    const renderConclusionEditor = () => (
        <div className="space-y-6">
            <div>
                <label className="label-text">总结标题</label>
                <input
                    type="text"
                    value={content.title || ''}
                    onChange={(e) => onUpdate({title: e.target.value})}
                    className="input-field text-lg"
                    placeholder="输入总结标题"
                />
            </div>

            <div>
                <label className="label-text">总结内容</label>
                <textarea
                    value={content.text || ''}
                    onChange={(e) => onUpdate({text: e.target.value})}
                    className="input-field resize-none"
                    rows={6}
                    placeholder="输入总结内容..."
                />
            </div>

            <div>
                <label className="label-text">要点回顾</label>
                <div className="space-y-2">
                    {bullets.map((bullet, index) => (
                        <motion.div
                            key={index}
                            initial={{opacity: 0, x: -10}}
                            animate={{opacity: 1, x: 0}}
                            className="flex items-center gap-2"
                        >
                            <GripVertical className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <input
                                type="text"
                                value={bullet}
                                onChange={(e) => handleBulletChange(index, e.target.value)}
                                className="input-field flex-1 text-sm"
                                placeholder={`要点 ${index + 1}`}
                            />
                            <button
                                onClick={() => handleRemoveBullet(index)}
                                className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </motion.div>
                    ))}
                    <button
                        onClick={handleAddBullet}
                        className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 transition-colors flex items-center justify-center gap-1"
                    >
                        <Plus className="w-4 h-4" />
            添加要点
                    </button>
                </div>
            </div>
        </div>
    );

    const renderEditorByType = () => {
        switch (type) {
        case 'title':
            return renderTitleEditor();
        case 'content':
            return renderContentEditor();
        case 'section':
            return renderSectionEditor();
        case 'chart':
            return renderChartEditor();
        case 'conclusion':
            return renderConclusionEditor();
        default:
            return renderContentEditor();
        }
    };

    return (
        <div className="space-y-6">
            {/* 幻灯片类型选择 */}
            <div className="bg-gray-50 rounded-xl p-4">
                <label className="text-sm font-medium text-gray-700 mb-3 block">
          幻灯片类型
                </label>
                <div className="grid grid-cols-5 gap-2">
                    {slideTypeOptions.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => onTypeChange(option.value)}
                            className={`
                flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all
                ${type === option.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }
              `}
                            title={option.description}
                        >
                            {option.icon}
                            <span className="text-xs font-medium">{option.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* 内容编辑器 */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-sm font-semibold text-gray-800 mb-4 pb-2 border-b">
          内容编辑
                </h3>
                {renderEditorByType()}
            </div>

            {/* 插图提示词 */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4 pb-2 border-b">
                    <ImageIcon className="w-4 h-4 text-blue-600" />
                    <h3 className="text-sm font-semibold text-gray-800">
            插图提示词
                    </h3>
                </div>
                <textarea
                    value={imagePrompt}
                    onChange={(e) => handleImagePromptChange(e.target.value)}
                    className="input-field resize-none"
                    rows={3}
                    placeholder="描述这页 PPT 需要的插图风格和内容..."
                />
                <p className="mt-2 text-xs text-gray-500">
          AI 将根据此提示词生成配图，留空则使用默认风格
                </p>
            </div>
        </div>
    );
}
