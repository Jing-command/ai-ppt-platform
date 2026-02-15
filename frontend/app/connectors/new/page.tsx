'use client';

import {useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion} from 'framer-motion';
import {ArrowLeft, Database, Loader2} from 'lucide-react';
import {ConnectorForm} from '@/components/connectors/ConnectorForm';
import {CreateConnectorRequest, UpdateConnectorRequest} from '@/types/connector';
import {createConnector} from '@/lib/api/connectors';
import {AxiosError} from 'axios';

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
  hidden: {opacity: 0, y: 30, scale: 0.96},
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

export default function NewConnectorPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (data: CreateConnectorRequest | UpdateConnectorRequest) => {
    setIsLoading(true);
    setError('');

    try {
      await createConnector(data as CreateConnectorRequest);
      router.push('/connectors');
    } catch (err) {
      const axiosError = err as AxiosError;

      if (axiosError.response?.status === 401) {
        router.push('/login');
        return;
      }

      if (axiosError.response?.status === 409) {
        setError('连接器名称已存在，请使用其他名称');
      } else if (axiosError.response?.status === 400) {
        const errorData = axiosError.response?.data as { message?: string };
        setError(errorData?.message || '请求参数错误');
      } else if (axiosError.response?.status === 422) {
        setError('表单验证失败，请检查输入信息');
      } else {
        setError('创建连接器失败，请稍后重试');
      }

      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/connectors');
  };

  return (
    <motion.div
      className="min-h-screen bg-[var(--color-background)]"
      variants={pageVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b border-[var(--color-border)]">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 gap-4">
            <motion.button
              onClick={() => router.push('/connectors')}
              whileHover={{x: -2}}
              whileTap={{scale: 0.95}}
              className="
                p-2 rounded-lg
                text-[var(--color-text-muted)]
                hover:text-[var(--color-text)]
                hover:bg-[var(--color-surface)]
                transition-colors duration-200
              "
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.button>

            <div className="flex items-center gap-3">
              <div
                className="
                  w-10 h-10 rounded-xl
                  bg-gradient-to-br from-blue-500 to-blue-600
                  flex items-center justify-center
                  shadow-md
                "
              >
                <Database className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-[var(--color-text)]">
                  新建连接器
                </h1>
                <p className="text-sm text-[var(--color-text-muted)]">
                  配置新的数据源连接
                </p>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区域 */}
      <main className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          className="
            bg-white rounded-xl
            shadow-[var(--shadow-card)]
            p-6 sm:p-8
          "
        >
          {/* 错误提示 */}
          {error && (
            <motion.div
              initial={{opacity: 0, y: -10}}
              animate={{opacity: 1, y: 0}}
              className="mb-6"
            >
              <div className="alert-error alert-error-icon">
                <Loader2 className="w-5 h-5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            </motion.div>
          )}

          {/* 表单 */}
          <ConnectorForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </motion.div>

        {/* 帮助信息 */}
        <motion.div
          initial={{opacity: 0}}
          animate={{opacity: 1}}
          transition={{delay: 0.3}}
          className="mt-8 text-center"
        >
          <p className="text-sm text-[var(--color-text-muted)]">
            需要帮助？
            <a
              href="#"
              className="text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
            >
              查看连接指南
            </a>
            或
            <a
              href="#"
              className="text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
            >
              联系支持团队
            </a>
          </p>
        </motion.div>
      </main>
    </motion.div>
  );
}
