'use client';

import {useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
    ArrowLeft,
    Sparkles,
    Loader2,
    FileText,
    Calendar,
    BarChart3,
    Briefcase,
    BookOpen,
    Lightbulb,
    ChevronDown,
    Check,
    Type,
    Palette,
    LayoutTemplate
} from 'lucide-react';
import {generateOutline} from '@/lib/api/outlines';
import {AxiosError} from 'axios';

// 分类配置
const categories = [
    {id: 'work', label: '工作汇报', icon: Briefcase},
    {id: 'education', label: '教育课件', icon: BookOpen},
    {id: 'business', label: '商业计划', icon: Lightbulb},
    {id: 'marketing', label: '市场营销', icon: BarChart3}
];

// 场景示例配置
import type {LucideIcon} from 'lucide-react';

const examples: Record<string, Array<{ id: string; title: string; icon: LucideIcon; content: string; description: string }>> = {
    work: [
        {
            id: 'weekly',
            title: '周报',
            icon: FileText,
            content: `生成一份本周工作总结周报，包含：
- 本周完成的主要任务（3-5项）
- 遇到的问题及解决方案
- 下周工作计划
- 需要协调的事项
适合向直属领导汇报，简洁专业`,
            description: '适合向直属领导汇报，简洁专业'
        },
        {
            id: 'daily',
            title: '日报',
            icon: Calendar,
            content: `制作今日工作日报，包含：
- 今日完成任务清单
- 工作时长分配
- 明日待办事项
- 工作心得/反思
适合每日站会或向上级同步进展`,
            description: '适合每日站会或向上级同步进展'
        },
        {
            id: 'monthly',
            title: '月度总结',
            icon: BarChart3,
            content: `创建月度工作复盘PPT，包含：
- 月度KPI完成情况
- 重点项目进展
- 数据成果展示
- 下月目标规划
适合部门会议或季度汇报使用`,
            description: '适合部门会议或季度汇报使用'
        }
    ],
    education: [
        {
            id: 'course',
            title: '课程教案',
            icon: BookOpen,
            content: `制作一份互动式课程教案PPT，包含：
- 教学目标与重难点
- 课程导入与互动环节
- 知识点讲解与案例分析
- 课堂练习与作业布置
适合中小学或培训机构教学使用`,
            description: '适合中小学或培训机构教学使用'
        },
        {
            id: 'lecture',
            title: '学术讲座',
            icon: Lightbulb,
            content: `设计学术专题讲座PPT，包含：
- 研究背景与意义
- 理论基础与方法论
- 实验数据与分析结果
- 结论与未来展望
适合高校学术报告或研讨会`,
            description: '适合高校学术报告或研讨会'
        },
        {
            id: 'training',
            title: '企业培训',
            icon: Briefcase,
            content: `创建新员工入职培训PPT，包含：
- 公司文化与价值观
- 规章制度与行为规范
- 岗位技能与工作流程
- 职业发展规划
适合企业HR部门培训使用`,
            description: '适合企业HR部门培训使用'
        }
    ],
    business: [
        {
            id: 'pitch',
            title: '融资路演',
            icon: Sparkles,
            content: `制作投资人路演PPT，包含：
- 项目简介与市场痛点
- 产品解决方案
- 商业模式与盈利预测
- 团队介绍与融资需求
适合创业团队融资展示使用`,
            description: '适合创业团队融资展示使用'
        },
        {
            id: 'plan',
            title: '商业计划书',
            icon: FileText,
            content: `编写完整商业计划书PPT，包含：
- 行业分析与市场规模
- 竞品分析与差异化优势
- 营销策略与运营规划
- 财务预测与风险评估
适合企业内部战略规划或合作洽谈`,
            description: '适合企业内部战略规划或合作洽谈'
        },
        {
            id: 'report',
            title: '年度汇报',
            icon: BarChart3,
            content: `制作公司年度总结汇报PPT，包含：
- 年度业绩回顾
- 关键项目成果展示
- 团队建设与文化建设
- 来年战略规划
适合公司年会或董事会汇报',`,
            description: '适合公司年会或董事会汇报'
        }
    ],
    marketing: [
        {
            id: 'campaign',
            title: '营销活动',
            icon: Sparkles,
            content: `设计营销活动策划PPT，包含：
- 活动目标与KPI设定
- 目标用户画像分析
- 创意方案与执行计划
- 预算分配与效果预估
适合市场部活动提案使用`,
            description: '适合市场部活动提案使用'
        },
        {
            id: 'brand',
            title: '品牌推广',
            icon: Lightbulb,
            content: `制作品牌升级推广方案PPT，包含：
- 品牌现状诊断
- 竞品品牌分析
- 品牌定位与视觉体系
- 推广渠道与内容策略
适合品牌部门战略提案',`,
            description: '适合品牌部门战略提案'
        },
        {
            id: 'analysis',
            title: '数据分析',
            icon: BarChart3,
            content: `创建市场数据分析报告PPT，包含：
- 数据来源与样本说明
- 用户行为与偏好分析
- 市场趋势与机会洞察
- 数据驱动的决策建议
适合数据分析师业务汇报使用`,
            description: '适合数据分析师业务汇报使用'
        }
    ]
};

// 语言选项
const languages = [
    {value: 'zh', label: '中文', flag: '🇨🇳'},
    {value: 'en', label: 'English', flag: '🇺🇸'}
];

// 风格选项
const styles = [
    {value: 'business', label: '商务专业', color: 'bg-blue-500'},
    {value: 'education', label: '教育简洁', color: 'bg-green-500'},
    {value: 'creative', label: '创意设计', color: 'bg-purple-500'},
    {value: 'technical', label: '技术严谨', color: 'bg-gray-600'}
];

export default function GenerateOutlinePage() {
    const router = useRouter();
    const [activeCategory, setActiveCategory] = useState('work');
    const [prompt, setPrompt] = useState('');
    const [numSlides, setNumSlides] = useState(15);
    const [language, setLanguage] = useState<'zh' | 'en'>('zh');
    const [style, setStyle] = useState<'business' | 'education' | 'creative' | 'technical'>('business');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showLangDropdown, setShowLangDropdown] = useState(false);
    const [showStyleDropdown, setShowStyleDropdown] = useState(false);

    const charCount = prompt.length;
    const isValid = charCount >= 10;

    const handleExampleClick = (content: string) => {
        setPrompt(content);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!isValid) {
            setError('请输入至少 10 个字符的描述');
            return;
        }

        setLoading(true);

        try {
            const response = await generateOutline({
                prompt: prompt.trim(),
                numSlides,
                language,
                style
            });

            alert(`生成任务已提交！\n任务 ID: ${response.taskId}\n预计时间: ${response.estimatedTime} 秒`);
            router.push('/outlines');
        } catch (err) {
            const axiosError = err as AxiosError;
            // 处理 401 错误或未登录情况
            if (axiosError.response?.status === 401 ||
          (err as Error).message?.includes('未登录')) {
                router.push('/login');
                return;
            }
            // 显示错误信息
            const errorMessage = (axiosError.response?.data as { message?: string })?.message
        || (err as Error).message
        || '生成失败，请稍后重试';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
            {/* 背景装饰 */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
            </div>

            {/* 导航栏 */}
            <motion.nav
                initial={{opacity: 0, y: -20}}
                animate={{opacity: 1, y: 0}}
                className="relative z-10 bg-white/80 backdrop-blur-md border-b border-gray-200/50"
            >
                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center">
                        <button
                            onClick={() => router.push('/outlines')}
                            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors group"
                        >
                            <div className="p-2 rounded-lg group-hover:bg-gray-100 transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                            </div>
                            <span className="font-medium">返回</span>
                        </button>
                        <div className="ml-auto flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <span className="font-semibold text-gray-900">AI PPT</span>
                        </div>
                    </div>
                </div>
            </motion.nav>

            {/* 主内容 */}
            <main className="relative z-10 max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
                {/* 标题区域 */}
                <motion.div
                    initial={{opacity: 0, y: 30}}
                    animate={{opacity: 1, y: 0}}
                    transition={{delay: 0.1, duration: 0.6}}
                    className="text-center mb-12"
                >
                    <motion.div
                        initial={{scale: 0.9, opacity: 0}}
                        animate={{scale: 1, opacity: 1}}
                        transition={{delay: 0.2, duration: 0.5}}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100/80 rounded-full mb-6"
                    >
                        <Sparkles className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-700">AI 智能大纲生成器</span>
                    </motion.div>
                    <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4 tracking-tight">
            输入主题，<span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">AI 为您规划每一页</span>
                    </h1>
                    <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            选择场景或自由输入，AI 将在几秒钟内为您生成完整的 PPT 大纲结构
                    </p>
                </motion.div>

                {/* 分类标签 */}
                <motion.div
                    initial={{opacity: 0, y: 20}}
                    animate={{opacity: 1, y: 0}}
                    transition={{delay: 0.3}}
                    className="flex justify-center mb-8"
                >
                    <div className="inline-flex bg-white/80 backdrop-blur-sm p-1.5 rounded-2xl shadow-lg shadow-gray-200/50 border border-gray-200/50">
                        {categories.map((category) => {
                            const Icon = category.icon;
                            const isActive = activeCategory === category.id;
                            return (
                                <motion.button
                                    key={category.id}
                                    onClick={() => setActiveCategory(category.id)}
                                    className={`relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
                                        isActive
                                            ? 'text-white'
                                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/50'
                                    }`}
                                    whileHover={{scale: 1.02}}
                                    whileTap={{scale: 0.98}}
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeCategory"
                                            className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl"
                                            transition={{type: 'spring', bounce: 0.2, duration: 0.6}}
                                        />
                                    )}
                                    <span className="relative z-10 flex items-center gap-2">
                                        <Icon className="w-4 h-4" />
                                        {category.label}
                                    </span>
                                </motion.button>
                            );
                        })}
                    </div>
                </motion.div>

                {/* 场景卡片 */}
                <motion.div
                    initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    transition={{delay: 0.4}}
                    className="mb-10"
                >
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeCategory}
                            initial={{opacity: 0, y: 20}}
                            animate={{opacity: 1, y: 0}}
                            exit={{opacity: 0, y: -20}}
                            transition={{duration: 0.3}}
                            className="grid grid-cols-1 sm:grid-cols-3 gap-4"
                        >
                            {examples[activeCategory]?.map((example, index) => {
                                const Icon = example.icon;
                                return (
                                    <motion.button
                                        key={example.id}
                                        onClick={() => handleExampleClick(example.content)}
                                        initial={{opacity: 0, y: 20}}
                                        animate={{opacity: 1, y: 0}}
                                        transition={{delay: index * 0.1}}
                                        whileHover={{
                                            scale: 1.03,
                                            y: -4,
                                            transition: {duration: 0.2}
                                        }}
                                        whileTap={{scale: 0.98}}
                                        className="group relative bg-white rounded-2xl p-5 shadow-sm hover:shadow-xl border border-gray-200/50 hover:border-blue-300/50 transition-all duration-300 text-left overflow-hidden"
                                    >
                                        {/* 悬停背景效果 */}
                                        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/0 via-blue-50/0 to-indigo-50/0 group-hover:from-blue-50/80 group-hover:via-blue-50/40 group-hover:to-indigo-50/60 transition-all duration-500" />

                                        <div className="relative z-10">
                                            <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                                                <Icon className="w-6 h-6 text-blue-600" />
                                            </div>
                                            <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-700 transition-colors">
                                                {example.title}
                                            </h3>
                                            <p className="text-sm text-gray-500 line-clamp-2">
                                                {example.description}
                                            </p>

                                            {/* 点击提示 */}
                                            <div className="mt-3 flex items-center gap-1 text-xs text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                                <Sparkles className="w-3 h-3" />
                                                <span>点击使用此模板</span>
                                            </div>
                                        </div>
                                    </motion.button>
                                );
                            })}
                        </motion.div>
                    </AnimatePresence>
                </motion.div>

                {/* 输入区域 */}
                <motion.div
                    initial={{opacity: 0, y: 30}}
                    animate={{opacity: 1, y: 0}}
                    transition={{delay: 0.5}}
                    className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-200/50 overflow-hidden"
                >
                    {/* 错误提示 */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{opacity: 0, height: 0}}
                                animate={{opacity: 1, height: 'auto'}}
                                exit={{opacity: 0, height: 0}}
                                className="bg-red-50 border-b border-red-100 px-6 py-4"
                            >
                                <p className="text-red-600 text-sm flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                                    {error}
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <form onSubmit={handleSubmit} className="p-6 sm:p-8">
                        {/* 输入框区域 - 对话气泡样式 */}
                        <div className="relative mb-6">
                            <motion.div
                                whileFocus={{scale: 1.01}}
                                className="relative"
                            >
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="输入你的 PPT 主题，例如：生成本周工作总结周报，包含本周完成的任务、遇到的问题及下周计划..."
                                    rows={5}
                                    disabled={loading}
                                    className="w-full px-6 py-5 bg-gray-50/50 rounded-2xl border-2 border-gray-200/50 text-gray-900 placeholder:text-gray-400 resize-none focus:outline-none focus:border-blue-400 focus:bg-white focus:shadow-[0_0_30px_rgba(59,130,246,0.15)] transition-all duration-300"
                                />

                                {/* AI 头像装饰 */}
                                <div className="absolute -top-3 -left-3 w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                            </motion.div>

                            {/* 字数统计 */}
                            <div className="flex justify-between items-center mt-3 px-1">
                                <p className="text-sm text-gray-400">
                                    {charCount === 0 ? '输入至少 10 个字符开始生成' : `已输入 ${charCount} 个字符`}
                                </p>
                                <div className={`flex items-center gap-2 text-sm transition-colors ${isValid ? 'text-green-600' : 'text-gray-400'}`}>
                                    {isValid && (
                                        <motion.div
                                            initial={{scale: 0}}
                                            animate={{scale: 1}}
                                            className="flex items-center gap-1"
                                        >
                                            <Check className="w-4 h-4" />
                                            <span>满足要求</span>
                                        </motion.div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* 设置区域 */}
                        <div className="flex flex-wrap items-center gap-4 mb-6">
                            {/* 页数选择 - 滑动条 */}
                            <div className="flex items-center gap-4 bg-gray-50 rounded-xl px-4 py-2.5 border border-gray-200/50 flex-1 min-w-[200px]">
                                <LayoutTemplate className="w-4 h-4 text-gray-500 flex-shrink-0" />
                                <span className="text-sm text-gray-600 flex-shrink-0">页数</span>
                                <div className="flex-1 flex items-center gap-3">
                                    <span className="text-xs text-gray-400 w-4">5</span>
                                    <input
                                        type="range"
                                        min={5}
                                        max={30}
                                        value={numSlides}
                                        onChange={(e) => setNumSlides(Number(e.target.value))}
                                        disabled={loading}
                                        className="flex-1 h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-blue-500 hover:accent-blue-600 transition-all"
                                        style={{
                                            background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((numSlides - 5) / (30 - 5)) * 100}%, #e5e7eb ${((numSlides - 5) / (30 - 5)) * 100}%, #e5e7eb 100%)`
                                        }}
                                    />
                                    <span className="text-xs text-gray-400 w-6">30</span>
                                </div>
                                <span className="w-8 text-center font-semibold text-blue-600 bg-blue-50 rounded-lg py-1 text-sm">{numSlides}</span>
                            </div>

                            {/* 语言选择 */}
                            <div className="relative">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowLangDropdown(!showLangDropdown);
                                        setShowStyleDropdown(false);
                                    }}
                                    disabled={loading}
                                    className="flex items-center gap-2 bg-gray-50 hover:bg-gray-100 rounded-xl px-4 py-2.5 border border-gray-200/50 text-sm text-gray-700 transition-colors"
                                >
                                    <Type className="w-4 h-4 text-gray-500" />
                                    <span>{languages.find(l => l.value === language)?.flag} {languages.find(l => l.value === language)?.label}</span>
                                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showLangDropdown ? 'rotate-180' : ''}`} />
                                </button>

                                <AnimatePresence>
                                    {showLangDropdown && (
                                        <motion.div
                                            initial={{opacity: 0, y: -10}}
                                            animate={{opacity: 1, y: 0}}
                                            exit={{opacity: 0, y: -10}}
                                            className="absolute top-full left-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200/50 py-2 min-w-[140px] z-20"
                                        >
                                            {languages.map((lang) => (
                                                <button
                                                    key={lang.value}
                                                    type="button"
                                                    onClick={() => {
                                                        setLanguage(lang.value as 'zh' | 'en');
                                                        setShowLangDropdown(false);
                                                    }}
                                                    className={`w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${language === lang.value ? 'text-blue-600 bg-blue-50' : 'text-gray-700'}`}
                                                >
                                                    <span>{lang.flag}</span>
                                                    <span>{lang.label}</span>
                                                    {language === lang.value && <Check className="w-4 h-4 ml-auto" />}
                                                </button>
                                            ))}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>

                            {/* 风格选择 */}
                            <div className="relative">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowStyleDropdown(!showStyleDropdown);
                                        setShowLangDropdown(false);
                                    }}
                                    disabled={loading}
                                    className="flex items-center gap-2 bg-gray-50 hover:bg-gray-100 rounded-xl px-4 py-2.5 border border-gray-200/50 text-sm text-gray-700 transition-colors"
                                >
                                    <Palette className="w-4 h-4 text-gray-500" />
                                    <span>{styles.find(s => s.value === style)?.label}</span>
                                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showStyleDropdown ? 'rotate-180' : ''}`} />
                                </button>

                                <AnimatePresence>
                                    {showStyleDropdown && (
                                        <motion.div
                                            initial={{opacity: 0, y: -10}}
                                            animate={{opacity: 1, y: 0}}
                                            exit={{opacity: 0, y: -10}}
                                            className="absolute top-full left-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200/50 py-2 min-w-[140px] z-20"
                                        >
                                            {styles.map((s) => (
                                                <button
                                                    key={s.value}
                                                    type="button"
                                                    onClick={() => {
                                                        setStyle(s.value as typeof style);
                                                        setShowStyleDropdown(false);
                                                    }}
                                                    className={`w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${style === s.value ? 'text-blue-600 bg-blue-50' : 'text-gray-700'}`}
                                                >
                                                    <span className={`w-2 h-2 rounded-full ${s.color}`} />
                                                    <span>{s.label}</span>
                                                    {style === s.value && <Check className="w-4 h-4 ml-auto" />}
                                                </button>
                                            ))}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* 生成按钮 */}
                        <motion.button
                            type="submit"
                            disabled={loading || !isValid}
                            whileHover={!loading && isValid ? {scale: 1.02} : {}}
                            whileTap={!loading && isValid ? {scale: 0.98} : {}}
                            className={`
                w-full py-4 px-6 rounded-2xl
                text-white font-semibold text-lg
                flex items-center justify-center gap-3
                transition-all duration-300
                ${isValid && !loading
            ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30'
            : 'bg-gray-300 cursor-not-allowed'
        }
              `}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    <span>AI 正在构思大纲...</span>
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-6 h-6" />
                                    <span>✨ AI 生成 {numSlides} 页大纲</span>
                                </>
                            )}
                        </motion.button>

                        {/* 底部提示 */}
                        <p className="text-center text-sm text-gray-400 mt-4">
              AI 将为每一页生成标题和内容建议，平均生成时间约 10-30 秒
                        </p>
                    </form>
                </motion.div>

                {/* 底部特性说明 */}
                <motion.div
                    initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    transition={{delay: 0.7}}
                    className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6 text-center"
                >
                    {[
                        {icon: Sparkles, title: '智能规划', desc: 'AI 自动分析主题，生成逻辑清晰的页面结构'},
                        {icon: LayoutTemplate, title: '多种场景', desc: '支持周报、课件、商业计划等多种应用场景'},
                        {icon: Check, title: '一键生成', desc: '输入主题即可生成，支持二次编辑调整'}
                    ].map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <div key={index} className="flex flex-col items-center">
                                <div className="w-12 h-12 bg-white rounded-2xl shadow-sm border border-gray-200/50 flex items-center justify-center mb-3">
                                    <Icon className="w-5 h-5 text-blue-500" />
                                </div>
                                <h4 className="font-medium text-gray-900 mb-1">{feature.title}</h4>
                                <p className="text-sm text-gray-500">{feature.desc}</p>
                            </div>
                        );
                    })}
                </motion.div>
            </main>
        </div>
    );
}
