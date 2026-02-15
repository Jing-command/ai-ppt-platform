/**
 * @fileoverview 注册页面
 * @author Frontend Agent
 * @date 2026-02-14
 */

'use client';

import {motion} from 'framer-motion';
import {RegisterForm} from '@/components/auth/RegisterForm';
import {FileText} from 'lucide-react';

// Animation variants
const pageVariants = {
    hidden: {opacity: 0},
    visible: {
        opacity: 1,
        transition: {
            duration: 0.4,
            ease: [0.4, 0, 0.2, 1] as const
        }
    }
};

const cardVariants = {
    hidden: {
        opacity: 0,
        y: 30,
        scale: 0.96
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            duration: 0.5,
            ease: [0.4, 0, 0.2, 1] as const
        }
    }
};

const logoVariants = {
    hidden: {opacity: 0, y: -10},
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.4,
            delay: 0.1,
            ease: [0.4, 0, 0.2, 1] as const
        }
    }
};

const footerVariants = {
    hidden: {opacity: 0},
    visible: {
        opacity: 1,
        transition: {
            duration: 0.4,
            delay: 0.3,
            ease: [0.4, 0, 0.2, 1] as const
        }
    }
};

export default function RegisterPage() {
    return (
        <motion.div
            className='min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8'
            style={{backgroundColor: 'var(--color-background)'}}
            variants={pageVariants}
            initial='hidden'
            animate='visible'
        >
            <div className='w-full max-w-[420px]'>
                {/* Logo 区域 */}
                <motion.div
                    className='text-center mb-8'
                    variants={logoVariants}
                    initial='hidden'
                    animate='visible'
                >
                    <motion.div
                        className='inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4'
                        style={{
                            background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                            boxShadow: '0 4px 14px 0 rgba(37, 99, 235, 0.25)'
                        }}
                        whileHover={{scale: 1.05}}
                        transition={{duration: 0.2}}
                    >
                        <FileText className='w-7 h-7 text-white' />
                    </motion.div>
                    <h1
                        className='text-2xl font-semibold tracking-tight'
                        style={{color: 'var(--color-text)'}}
                    >
            创建账户
                    </h1>
                    <p
                        className='mt-2 text-sm'
                        style={{color: 'var(--color-text-muted)'}}
                    >
            注册 AI PPT 平台，开始智能演示
                    </p>
                </motion.div>

                {/* 注册卡片 */}
                <motion.div
                    className='rounded-xl p-8'
                    style={{
                        backgroundColor: 'var(--color-card)',
                        boxShadow: 'var(--shadow-card)'
                    }}
                    variants={cardVariants}
                    initial='hidden'
                    animate='visible'
                >
                    <RegisterForm />
                </motion.div>

                {/* 底部链接 */}
                <motion.div
                    className='mt-6 text-center'
                    variants={footerVariants}
                    initial='hidden'
                    animate='visible'
                >
                    <p
                        className='text-sm'
                        style={{color: 'var(--color-text-muted)'}}
                    >
            已有账户？{' '}
                        <motion.a
                            href='/login'
                            className='font-medium'
                            style={{color: 'var(--color-primary)'}}
                            whileHover={{color: 'var(--color-primary-hover)'}}
                            transition={{duration: 0.15}}
                        >
              立即登录
                        </motion.a>
                    </p>
                </motion.div>

                {/* 页脚信息 */}
                <motion.p
                    className='mt-8 text-center text-xs'
                    style={{color: 'var(--color-text-placeholder)'}}
                    variants={footerVariants}
                    initial='hidden'
                    animate='visible'
                >
          注册即表示您同意我们的{' '}
                    <a href='#' className='underline hover:text-[var(--color-text-muted)] transition-colors'>
            服务条款
                    </a>{' '}
          和{' '}
                    <a href='#' className='underline hover:text-[var(--color-text-muted)] transition-colors'>
            隐私政策
                    </a>
                </motion.p>
            </div>
        </motion.div>
    );
}
