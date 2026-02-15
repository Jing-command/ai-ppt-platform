'use client';

import {useState} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {z} from 'zod';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {Mail, Lock, Loader2, AlertCircle, Eye, EyeOff} from 'lucide-react';
import {login, saveAuthData} from '@/lib/api/auth';
import {AxiosError} from 'axios';

// Zod 验证 schema
const loginSchema = z.object({
    email: z.string().email('请输入有效的邮箱地址'),
    password: z.string().min(6, '密码至少6位')
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginFormProps {
  className?: string;
}

// Animation variants
const containerVariants = {
    hidden: {opacity: 0},
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.1
        }
    }
};

const itemVariants = {
    hidden: {opacity: 0, y: 10},
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.3,
            ease: 'easeOut' as const
        }
    }
};

const errorVariants = {
    hidden: {opacity: 0, height: 0, marginBottom: 0},
    visible: {
        opacity: 1,
        height: 'auto',
        marginBottom: 16,
        transition: {
            duration: 0.2,
            ease: 'easeOut' as const
        }
    },
    exit: {
        opacity: 0,
        height: 0,
        marginBottom: 0,
        transition: {
            duration: 0.15
        }
    }
};

const shakeVariants = {
    shake: {
        x: [-4, 4, -4, 4, -2, 2, 0],
        transition: {duration: 0.4}
    }
};

export function LoginForm({className}: LoginFormProps) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [focusedField, setFocusedField] = useState<string | null>(null);

    const {
        register,
        handleSubmit,
        formState: {errors}
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: '',
            password: ''
        }
    });

    const onSubmit = async (data: LoginFormData) => {
        setIsLoading(true);
        setErrorMessage('');

        try {
            const response = await login(data);
            saveAuthData(response);
            router.push('/dashboard');
        } catch (error) {
            if (error instanceof AxiosError) {
                const status = error.response?.status;
                switch (status) {
                case 401:
                    setErrorMessage('邮箱或密码错误');
                    break;
                case 422:
                    setErrorMessage('表单验证错误，请检查输入');
                    break;
                case 500:
                    setErrorMessage('服务器错误，请稍后重试');
                    break;
                default:
                    setErrorMessage('登录失败，请稍后重试');
                }
            } else {
                setErrorMessage('网络错误，请检查网络连接');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <motion.form
            onSubmit={handleSubmit(onSubmit)}
            className={`space-y-5 ${className || ''}`}
            variants={containerVariants}
            initial="hidden"
            animate="visible"
        >
            {/* 错误提示区域 */}
            <AnimatePresence mode="wait">
                {errorMessage && (
                    <motion.div
                        variants={errorVariants}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                        className="overflow-hidden"
                    >
                        <motion.div
                            animate="shake"
                            variants={shakeVariants}
                            className="flex items-start gap-3 p-4 rounded-lg bg-[var(--color-error-light)] border border-[var(--color-error-border)]"
                        >
                            <AlertCircle className="w-5 h-5 text-[var(--color-error)] flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-[var(--color-error)]">{errorMessage}</span>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* 邮箱输入框 */}
            <motion.div variants={itemVariants}>
                <label
                    htmlFor="email"
                    className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5"
                >
          邮箱地址
                </label>
                <motion.div
                    animate={{
                        scale: focusedField === 'email' ? 1.01 : 1
                    }}
                    transition={{duration: 0.2, ease: 'easeOut' as const}}
                    className="relative"
                >
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-[var(--color-text-placeholder)]" />
                    </div>
                    <input
                        {...register('email')}
                        type="email"
                        id="email"
                        autoComplete="email"
                        disabled={isLoading}
                        onFocus={() => setFocusedField('email')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-11 pr-4 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]"
                        style={{
                            boxShadow: focusedField === 'email' ? 'var(--shadow-focus)' : undefined
                        }}
                        placeholder="name@company.com"
                    />
                </motion.div>
                {errors.email && (
                    <motion.p
                        initial={{opacity: 0, y: -5}}
                        animate={{opacity: 1, y: 0}}
                        className="mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1"
                    >
                        <AlertCircle className="w-3.5 h-3.5" />
                        {errors.email.message}
                    </motion.p>
                )}
            </motion.div>

            {/* 密码输入框 */}
            <motion.div variants={itemVariants}>
                <div className="flex items-center justify-between mb-1.5">
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-[var(--color-text-secondary)]"
                    >
            密码
                    </label>
                    <a
                        href="#"
                        className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors"
                    >
            忘记密码？
                    </a>
                </div>
                <motion.div
                    animate={{
                        scale: focusedField === 'password' ? 1.01 : 1
                    }}
                    transition={{duration: 0.2, ease: 'easeOut' as const}}
                    className="relative"
                >
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-[var(--color-text-placeholder)]" />
                    </div>
                    <input
                        {...register('password')}
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        autoComplete="current-password"
                        disabled={isLoading}
                        onFocus={() => setFocusedField('password')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full pl-11 pr-11 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]"
                        style={{
                            boxShadow: focusedField === 'password' ? 'var(--shadow-focus)' : undefined
                        }}
                        placeholder="输入您的密码"
                    />
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-[var(--color-text-placeholder)]
                       hover:text-[var(--color-text-muted)] transition-colors focus:outline-none"
                    >
                        {showPassword ? (
                            <EyeOff className="h-5 w-5" />
                        ) : (
                            <Eye className="h-5 w-5" />
                        )}
                    </button>
                </motion.div>
                {errors.password && (
                    <motion.p
                        initial={{opacity: 0, y: -5}}
                        animate={{opacity: 1, y: 0}}
                        className="mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1"
                    >
                        <AlertCircle className="w-3.5 h-3.5" />
                        {errors.password.message}
                    </motion.p>
                )}
            </motion.div>

            {/* 登录按钮 */}
            <motion.div variants={itemVariants} className="pt-2">
                <motion.button
                    type="submit"
                    disabled={isLoading}
                    whileHover={{scale: isLoading ? 1 : 1.01}}
                    whileTap={{scale: isLoading ? 1 : 0.98}}
                    transition={{duration: 0.1}}
                    className="w-full flex items-center justify-center px-4 py-3
                     text-white font-medium text-base rounded-lg
                     bg-gradient-to-r from-blue-600 to-blue-500
                     hover:from-blue-700 hover:to-blue-600
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                     disabled:opacity-70 disabled:cursor-not-allowed
                     shadow-md hover:shadow-lg
                     transition-shadow duration-200"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="animate-spin mr-2 h-5 w-5" />
                            <span>登录中...</span>
                        </>
                    ) : (
                        <span>登录</span>
                    )}
                </motion.button>
            </motion.div>
        </motion.form>
    );
}
