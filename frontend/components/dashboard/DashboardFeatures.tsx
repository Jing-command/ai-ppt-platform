'use client';

import Link from 'next/link';
import {motion} from 'framer-motion';
import {Lightbulb, BarChart3, ArrowRight, Sparkles} from 'lucide-react';

const features = [
    {
        icon: Lightbulb,
        title: '提示词技巧',
        desc: '掌握 AI 提示词编写技巧，让生成的大纲更加精准、专业。系统提供多种场景模板和优化建议，助你快速获得理想的PPT结构。',
        href: '/tips/prompts',
        gradient: 'from-amber-500 to-orange-600',
        bgGradient: 'from-amber-50 to-orange-50',
        iconBg: 'bg-gradient-to-br from-amber-400 to-orange-500',
        tags: ['场景模板', '优化建议', '智能推荐'],
        tagColor: 'bg-amber-100 text-amber-700'
    },
    {
        icon: BarChart3,
        title: '数据可视化',
        desc: '一键将数据转化为精美图表，支持柱状图、折线图、饼图等20+图表类型。AI智能推荐最佳图表，让你的数据会说话。',
        href: '/tips/visualization',
        gradient: 'from-blue-500 to-indigo-600',
        bgGradient: 'from-blue-50 to-indigo-50',
        iconBg: 'bg-gradient-to-br from-blue-400 to-indigo-500',
        tags: ['20+ 图表', 'AI推荐', '一键生成'],
        tagColor: 'bg-blue-100 text-blue-700'
    }
];

export function DashboardFeatures() {
    return (
        <motion.section
            initial={{opacity: 0, y: 20}}
            animate={{opacity: 1, y: 0}}
            transition={{delay: 0.3, duration: 0.1}}
            className="mb-10"
        >
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-gray-900">智能辅助功能</h2>
                    <p className="text-sm text-gray-500">让 AI 助你打造更专业的演示文稿</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {features.map((feature, index) => {
                    const Icon = feature.icon;
                    return (
                        <motion.div
                            key={feature.title}
                            initial={{opacity: 0, y: 20}}
                            animate={{opacity: 1, y: 0}}
                            transition={{delay: 0.4 + index * 0.1, duration: 0.1}}
                            whileHover={{y: -4, transition: {duration: 0.1}}}
                        >
                            <Link
                                href={feature.href}
                                className="group block relative overflow-hidden rounded-2xl bg-white shadow-lg shadow-gray-200/50 border border-gray-100 hover:shadow-xl hover:border-gray-200 transition-all duration-100"
                            >
                                <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-br ${feature.bgGradient} opacity-50 rounded-bl-full group-hover:opacity-80 transition-opacity duration-100`} />

                                <div className="relative p-6">
                                    <div className="flex items-start gap-4 mb-4">
                                        <div className={`w-14 h-14 rounded-xl ${feature.iconBg} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-100`}>
                                            <Icon className="w-7 h-7 text-white" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                                                {feature.title}
                                            </h3>
                                            <div className="flex items-center gap-1 mt-1 text-sm text-blue-600 font-medium">
                                                <span>立即体验</span>
                                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-100" />
                                            </div>
                                        </div>
                                    </div>

                                    <p className="text-sm text-gray-600 leading-relaxed">
                                        {feature.desc}
                                    </p>

                                    <div className="flex flex-wrap gap-2 mt-4">
                                        {feature.tags.map((tag) => (
                                            <span key={tag} className={`px-2.5 py-1 text-xs font-medium ${feature.tagColor} rounded-full`}>
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </Link>
                        </motion.div>
                    );
                })}
            </div>
        </motion.section>
    );
}
