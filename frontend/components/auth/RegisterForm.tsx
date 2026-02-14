/**
 * @fileoverview 注册表单组件
 * @author Frontend Agent
 * @date 2026-02-14
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Mail,
  Lock,
  Loader2,
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
} from 'lucide-react';
import { register as registerUser, saveAuthData, login } from '@/lib/api/auth';
import { AxiosError } from 'axios';

// Zod 验证 schema
const registerSchema = z
  .object({
    name: z
      .string()
      .min(2, '用户名至少2个字符')
      .max(20, '用户名最多20个字符'),
    email: z.string().email('请输入有效的邮箱地址'),
    password: z.string().min(6, '密码至少6位'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: '两次输入的密码不一致',
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

interface RegisterFormProps {
  className?: string;
}

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const,
    },
  },
};

const errorVariants = {
  hidden: { opacity: 0, height: 0, marginBottom: 0 },
  visible: {
    opacity: 1,
    height: 'auto',
    marginBottom: 16,
    transition: {
      duration: 0.2,
      ease: 'easeOut' as const,
    },
  },
  exit: {
    opacity: 0,
    height: 0,
    marginBottom: 0,
    transition: {
      duration: 0.15,
    },
  },
};

const shakeVariants = {
  shake: {
    x: [-4, 4, -4, 4, -2, 2, 0],
    transition: { duration: 0.4 },
  },
};

export function RegisterForm({ className }: RegisterFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      // 调用注册 API
      await registerUser({
        name: data.name,
        email: data.email,
        password: data.password,
      });

      // 注册成功后自动登录
      try {
        const loginResponse = await login({
          email: data.email,
          password: data.password,
        });
        saveAuthData(loginResponse);
        setIsSuccess(true);

        // 延迟跳转，显示成功状态
        setTimeout(() => {
          router.push('/dashboard');
        }, 800);
      } catch {
        // 自动登录失败，跳转到登录页面
        router.push('/login?registered=true');
      }
    } catch (error) {
      if (error instanceof AxiosError) {
        const status = error.response?.status;
        const detail = error.response?.data?.detail;

        switch (status) {
          case 409:
            setErrorMessage(detail || '该邮箱已被注册');
            break;
          case 422:
            setErrorMessage(detail || '表单验证错误，请检查输入');
            break;
          case 500:
            setErrorMessage('服务器错误，请稍后重试');
            break;
          default:
            setErrorMessage(detail || '注册失败，请稍后重试');
        }
      } else {
        setErrorMessage('网络错误，请检查网络连接');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 成功状态
  if (isSuccess) {
    return (
      <motion.div
        className='flex flex-col items-center justify-center py-8'
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <CheckCircle2 className='w-16 h-16 text-green-500 mb-4' />
        </motion.div>
        <h3 className='text-lg font-medium text-[var(--color-text)]'>
          注册成功！
        </h3>
        <p className='text-sm text-[var(--color-text-muted)] mt-2'>
          正在跳转至工作台...
        </p>
      </motion.div>
    );
  }

  return (
    <motion.form
      onSubmit={handleSubmit(onSubmit)}
      className={`space-y-5 ${className || ''}`}
      variants={containerVariants}
      initial='hidden'
      animate='visible'
    >
      {/* 错误提示区域 */}
      <AnimatePresence mode='wait'>
        {errorMessage && (
          <motion.div
            variants={errorVariants}
            initial='hidden'
            animate='visible'
            exit='exit'
            className='overflow-hidden'
          >
            <motion.div
              animate='shake'
              variants={shakeVariants}
              className='flex items-start gap-3 p-4 rounded-lg bg-[var(--color-error-light)] border border-[var(--color-error-border)]'
            >
              <AlertCircle className='w-5 h-5 text-[var(--color-error)] flex-shrink-0 mt-0.5' />
              <span className='text-sm text-[var(--color-error)]'>{errorMessage}</span>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 用户名输入框 */}
      <motion.div variants={itemVariants}>
        <label
          htmlFor='name'
          className='block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5'
        >
          用户名
        </label>
        <motion.div
          animate={{
            scale: focusedField === 'name' ? 1.01 : 1,
          }}
          transition={{ duration: 0.2, ease: 'easeOut' as const }}
          className='relative'
        >
          <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none'>
            <User className='h-5 w-5 text-[var(--color-text-placeholder)]' />
          </div>
          <input
            {...register('name')}
            type='text'
            id='name'
            autoComplete='name'
            disabled={isLoading}
            onFocus={() => setFocusedField('name')}
            onBlur={() => setFocusedField(null)}
            className='w-full pl-11 pr-4 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]'
            style={{
              boxShadow: focusedField === 'name' ? 'var(--shadow-focus)' : undefined,
            }}
            placeholder='请输入您的用户名'
          />
        </motion.div>
        {errors.name && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className='mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1'
          >
            <AlertCircle className='w-3.5 h-3.5' />
            {errors.name.message}
          </motion.p>
        )}
      </motion.div>

      {/* 邮箱输入框 */}
      <motion.div variants={itemVariants}>
        <label
          htmlFor='email'
          className='block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5'
        >
          邮箱地址
        </label>
        <motion.div
          animate={{
            scale: focusedField === 'email' ? 1.01 : 1,
          }}
          transition={{ duration: 0.2, ease: 'easeOut' as const }}
          className='relative'
        >
          <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none'>
            <Mail className='h-5 w-5 text-[var(--color-text-placeholder)]' />
          </div>
          <input
            {...register('email')}
            type='email'
            id='email'
            autoComplete='email'
            disabled={isLoading}
            onFocus={() => setFocusedField('email')}
            onBlur={() => setFocusedField(null)}
            className='w-full pl-11 pr-4 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]'
            style={{
              boxShadow: focusedField === 'email' ? 'var(--shadow-focus)' : undefined,
            }}
            placeholder='name@company.com'
          />
        </motion.div>
        {errors.email && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className='mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1'
          >
            <AlertCircle className='w-3.5 h-3.5' />
            {errors.email.message}
          </motion.p>
        )}
      </motion.div>

      {/* 密码输入框 */}
      <motion.div variants={itemVariants}>
        <label
          htmlFor='password'
          className='block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5'
        >
          密码
        </label>
        <motion.div
          animate={{
            scale: focusedField === 'password' ? 1.01 : 1,
          }}
          transition={{ duration: 0.2, ease: 'easeOut' as const }}
          className='relative'
        >
          <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none'>
            <Lock className='h-5 w-5 text-[var(--color-text-placeholder)]' />
          </div>
          <input
            {...register('password')}
            type={showPassword ? 'text' : 'password'}
            id='password'
            autoComplete='new-password'
            disabled={isLoading}
            onFocus={() => setFocusedField('password')}
            onBlur={() => setFocusedField(null)}
            className='w-full pl-11 pr-11 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]'
            style={{
              boxShadow: focusedField === 'password' ? 'var(--shadow-focus)' : undefined,
            }}
            placeholder='至少6位字符'
          />
          <button
            type='button'
            onClick={() => setShowPassword(!showPassword)}
            className='absolute inset-y-0 right-0 pr-4 flex items-center text-[var(--color-text-placeholder)]
                       hover:text-[var(--color-text-muted)] transition-colors focus:outline-none'
          >
            {showPassword ? (
              <EyeOff className='h-5 w-5' />
            ) : (
              <Eye className='h-5 w-5' />
            )}
          </button>
        </motion.div>
        {errors.password && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className='mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1'
          >
            <AlertCircle className='w-3.5 h-3.5' />
            {errors.password.message}
          </motion.p>
        )}
      </motion.div>

      {/* 确认密码输入框 */}
      <motion.div variants={itemVariants}>
        <label
          htmlFor='confirmPassword'
          className='block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5'
        >
          确认密码
        </label>
        <motion.div
          animate={{
            scale: focusedField === 'confirmPassword' ? 1.01 : 1,
          }}
          transition={{ duration: 0.2, ease: 'easeOut' as const }}
          className='relative'
        >
          <div className='absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none'>
            <Lock className='h-5 w-5 text-[var(--color-text-placeholder)]' />
          </div>
          <input
            {...register('confirmPassword')}
            type={showConfirmPassword ? 'text' : 'password'}
            id='confirmPassword'
            autoComplete='new-password'
            disabled={isLoading}
            onFocus={() => setFocusedField('confirmPassword')}
            onBlur={() => setFocusedField(null)}
            className='w-full pl-11 pr-11 py-3 bg-white border border-[var(--color-border)] rounded-lg
                       text-[var(--color-text)] placeholder-[var(--color-text-placeholder)]
                       shadow-[var(--shadow-input)]
                       transition-all duration-200 ease-out
                       hover:border-[var(--color-border-hover)]
                       focus:outline-none focus:border-[var(--color-primary)]
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-[var(--color-surface)]'
            style={{
              boxShadow: focusedField === 'confirmPassword' ? 'var(--shadow-focus)' : undefined,
            }}
            placeholder='再次输入密码'
          />
          <button
            type='button'
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className='absolute inset-y-0 right-0 pr-4 flex items-center text-[var(--color-text-placeholder)]
                       hover:text-[var(--color-text-muted)] transition-colors focus:outline-none'
          >
            {showConfirmPassword ? (
              <EyeOff className='h-5 w-5' />
            ) : (
              <Eye className='h-5 w-5' />
            )}
          </button>
        </motion.div>
        {errors.confirmPassword && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className='mt-1.5 text-sm text-[var(--color-error)] flex items-center gap-1'
          >
            <AlertCircle className='w-3.5 h-3.5' />
            {errors.confirmPassword.message}
          </motion.p>
        )}
      </motion.div>

      {/* 注册按钮 */}
      <motion.div variants={itemVariants} className='pt-2'>
        <motion.button
          type='submit'
          disabled={isLoading}
          whileHover={{ scale: isLoading ? 1 : 1.01 }}
          whileTap={{ scale: isLoading ? 1 : 0.98 }}
          transition={{ duration: 0.1 }}
          className='w-full flex items-center justify-center px-4 py-3
                     text-white font-medium text-base rounded-lg
                     bg-gradient-to-r from-blue-600 to-blue-500
                     hover:from-blue-700 hover:to-blue-600
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                     disabled:opacity-70 disabled:cursor-not-allowed
                     shadow-md hover:shadow-lg
                     transition-shadow duration-200'
        >
          {isLoading ? (
            <>
              <Loader2 className='animate-spin mr-2 h-5 w-5' />
              <span>注册中...</span>
            </>
          ) : (
            <span>创建账户</span>
          )}
        </motion.button>
      </motion.div>
    </motion.form>
  );
}
