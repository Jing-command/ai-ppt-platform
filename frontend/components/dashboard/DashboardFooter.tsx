'use client';

import {motion} from 'framer-motion';
import {Sparkles} from 'lucide-react';

export function DashboardFooter() {
    return (
        <motion.footer
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            transition={{delay: 0.8, duration: 0.3}}
            className="mt-10 py-6 border-t border-gray-200/50"
        >
            <div className="flex flex-col items-center gap-1">
                {/* 版权信息 */}
                <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Sparkles className="w-4 h-4 text-violet-500" />
                    <span>© 2026 AI PPT</span>
                    <span className="text-gray-300">|</span>
                    <span>All Rights Reserved.</span>
                </div>

                {/* 标语 */}
                <p className="text-xs text-gray-400">
          AI 驱动的智能演示文稿生成平台 · 让创作更简单
                </p>
            </div>
        </motion.footer>
    );
}
