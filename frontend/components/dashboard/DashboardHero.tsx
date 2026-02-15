'use client';

import {motion} from 'framer-motion';
import {Zap} from 'lucide-react';
import {User} from '@/types/auth';
import {getGreeting, getInitials} from '@/utils/helpers';

interface DashboardHeroProps {
  user: User | null;
}

export function DashboardHero({user}: DashboardHeroProps) {
    return (
        <motion.section className="mb-10">
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 p-8 sm:p-12 shadow-2xl shadow-blue-500/25">
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-500/30 rounded-full blur-3xl" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl" />
                </div>

                <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                    <div className="flex-1">
                        <motion.div
                            initial={{opacity: 0, x: -20}}
                            animate={{opacity: 1, x: 0}}
                            transition={{delay: 0.3, duration: 0.1}}
                            className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 backdrop-blur-sm rounded-full mb-4"
                        >
                            <Zap className="w-4 h-4 text-yellow-300" />
                            <span className="text-sm font-medium text-white/90">
                                {getGreeting()}，开启高效创作
                            </span>
                        </motion.div>
                        <motion.h1
                            initial={{opacity: 0, y: 20}}
                            animate={{opacity: 1, y: 0}}
                            transition={{delay: 0.4, duration: 0.1}}
                            className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3"
                        >
              欢迎回来，{user?.name || '用户'}！
                        </motion.h1>
                        <motion.p
                            initial={{opacity: 0, y: 20}}
                            animate={{opacity: 1, y: 0}}
                            transition={{delay: 0.5, duration: 0.1}}
                            className="text-lg text-white/80 max-w-xl"
                        >
              今天想要创建什么样的演示文稿？让 AI 助你轻松完成专业设计。
                        </motion.p>
                    </div>

                    <motion.div
                        initial={{opacity: 0, scale: 0.8}}
                        animate={{opacity: 1, scale: 1}}
                        transition={{delay: 0.5, type: 'tween', duration: 0.1}}
                        className="flex-shrink-0"
                    >
                        <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white/20 backdrop-blur-sm border-2 border-white/30 flex items-center justify-center shadow-xl">
                            <span className="text-3xl sm:text-4xl font-bold text-white">
                                {getInitials(user?.name)}
                            </span>
                        </div>
                    </motion.div>
                </div>
            </div>
        </motion.section>
    );
}
