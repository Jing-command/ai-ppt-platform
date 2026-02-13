'use client';

import { useState, useEffect } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Cloud, ChevronDown, AlertCircle, Loader2 } from 'lucide-react';
import {
  ConnectorType,
  Connector,
  CreateConnectorRequest,
  UpdateConnectorRequest,
  CONNECTOR_TYPE_CONFIGS,
  ConnectorTypeConfig,
} from '@/types/connector';
import { TestConnectionButton } from './TestConnectionButton';

// 动态生成验证 schema
const createConnectorSchema = (typeConfig: ConnectorTypeConfig | null) => {
  if (!typeConfig) {
    return z.object({
      name: z.string().min(1, '请输入连接器名称').max(100, '名称最多100个字符'),
      type: z.string().min(1, '请选择连接器类型'),
      description: z.string().max(500, '描述最多500个字符').optional(),
    });
  }

  const configShape: Record<string, unknown> = {};
  typeConfig.fields.forEach((field) => {
    if (field.type === 'number') {
      configShape[field.name] = field.required
        ? z.number({ invalid_type_error: `请输入有效的${field.label}` })
            .min(1, `${field.label}必须大于0`)
        : z.number().optional();
    } else {
      configShape[field.name] = field.required
        ? z.string().min(1, `请输入${field.label}`)
        : z.string().optional();
    }
  });

  return z.object({
    name: z.string().min(1, '请输入连接器名称').max(100, '名称最多100个字符'),
    type: z.string().min(1, '请选择连接器类型'),
    description: z.string().max(500, '描述最多500个字符').optional(),
    config: z.object(configShape),
  });
};

interface ConnectorFormProps {
  initialData?: Connector;
  onSubmit: (data: CreateConnectorRequest | UpdateConnectorRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
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
      ease: [0.4, 0, 0.2, 1] as const,
    },
  },
};

const typeIcons: Record<ConnectorType, React.ReactNode> = {
  mysql: <Database className="w-5 h-5" />,
  postgresql: <Database className="w-5 h-5" />,
  mongodb: <Database className="w-5 h-5" />,
  salesforce: <Cloud className="w-5 h-5" />,
  csv: <Database className="w-5 h-5" />,
  api: <Cloud className="w-5 h-5" />,
};

export function ConnectorForm({ initialData, onSubmit, onCancel, isLoading }: ConnectorFormProps) {
  const [selectedType, setSelectedType] = useState<ConnectorType | ''>(initialData?.type || '');
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);
  const [testConfig, setTestConfig] = useState<Record<string, unknown> | null>(null);

  const typeConfig = selectedType ? CONNECTOR_TYPE_CONFIGS[selectedType] : null;
  const schema = createConnectorSchema(typeConfig);

  const {
    register,
    handleSubmit,
    formState: { errors },

    setValue,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    reset,
    control,
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initialData?.name || '',
      type: initialData?.type || '',
      description: initialData?.description || '',
      config: initialData?.config || {},
    },
  });

  // 监听配置变化用于测试
  const watchedConfig = useWatch({ control, name: 'config' });

  useEffect(() => {
    if (selectedType && watchedConfig) {
      setTestConfig(watchedConfig);
    }
  }, [selectedType, watchedConfig]);

  const handleTypeSelect = (type: ConnectorType) => {
    setSelectedType(type);
    setValue('type', type);
    setShowTypeDropdown(false);

    // 重置配置
    const config: Record<string, unknown> = {};
    const newTypeConfig = CONNECTOR_TYPE_CONFIGS[type];
    newTypeConfig?.fields.forEach((field) => {
      config[field.name] = field.defaultValue !== undefined ? field.defaultValue : '';
    });
    setValue('config', config);
  };

  const handleFormSubmit = async (data: CreateConnectorRequest | UpdateConnectorRequest) => {
    // 转换数字字段
    if (typeConfig) {
      typeConfig.fields.forEach((field) => {
        if (field.type === 'number' && data.config[field.name]) {
          data.config[field.name] = Number(data.config[field.name]);
        }
      });
    }

    await onSubmit(data as CreateConnectorRequest);
  };

  const availableTypes: ConnectorType[] = ['mysql', 'salesforce', 'postgresql'];

  return (
    <motion.form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* 连接器名称 */}
      <motion.div variants={itemVariants}>
        <label className="form-label">
          连接器名称 <span className="text-red-500">*</span>
        </label>
        <input
          {...register('name')}
          type="text"
          placeholder="例如：销售数据库"
          className="form-input"
          disabled={isLoading}
        />
        {errors.name && (
          <p className="form-error">
            <AlertCircle className="w-3.5 h-3.5" />
            {errors.name.message}
          </p>
        )}
      </motion.div>

      {/* 连接器类型 */}
      <motion.div variants={itemVariants} className="relative">
        <label className="form-label">
          连接器类型 <span className="text-red-500">*</span>
        </label>
        <button
          type="button"
          onClick={() => setShowTypeDropdown(!showTypeDropdown)}
          disabled={isLoading || !!initialData}
          className={`
            w-full px-4 py-3 bg-white border rounded-lg
            text-left flex items-center justify-between
            transition-all duration-200
            ${initialData ? 'opacity-60 cursor-not-allowed' : 'hover:border-[var(--color-border-hover)]'}
            ${showTypeDropdown ? 'border-[var(--color-primary)] ring-2 ring-blue-100' : 'border-[var(--color-border)]'}
          `}
        >
          <div className="flex items-center gap-3">
            {selectedType ? (
              <>
                <div className="text-[var(--color-text-muted)]">
                  {typeIcons[selectedType as ConnectorType]}
                </div>
                <span className="text-[var(--color-text)]">
                  {CONNECTOR_TYPE_CONFIGS[selectedType]?.label}
                </span>
              </>
            ) : (
              <span className="text-[var(--color-text-placeholder)]">请选择连接器类型</span>
            )}
          </div>
          <ChevronDown
            className={`w-5 h-5 text-[var(--color-text-muted)] transition-transform duration-200 ${
              showTypeDropdown ? 'rotate-180' : ''
            }`}
          />
        </button>

        {/* 下拉菜单 */}
        <AnimatePresence>
          {showTypeDropdown && !initialData && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="
                absolute z-10 w-full mt-1
                bg-white border border-[var(--color-border)] rounded-lg
                shadow-lg overflow-hidden
              "
            >
              {availableTypes.map((type) => {
                const config = CONNECTOR_TYPE_CONFIGS[type];
                return (
                  <button
                    key={type}
                    type="button"
                    onClick={() => handleTypeSelect(type)}
                    className="
                      w-full px-4 py-3 flex items-center gap-3
                      hover:bg-[var(--color-surface)]
                      transition-colors duration-150
                      text-left
                    "
                  >
                    <div className="text-[var(--color-text-muted)]">{typeIcons[type]}</div>
                    <div>
                      <p className="font-medium text-[var(--color-text)]">{config.label}</p>
                      <p className="text-xs text-[var(--color-text-muted)]">{config.description}</p>
                    </div>
                  </button>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>

        {errors.type && (
          <p className="form-error">
            <AlertCircle className="w-3.5 h-3.5" />
            {errors.type.message}
          </p>
        )}
      </motion.div>

      {/* 描述 */}
      <motion.div variants={itemVariants}>
        <label className="form-label">描述</label>
        <textarea
          {...register('description')}
          rows={3}
          placeholder="可选：添加连接器的描述信息"
          className="form-input resize-none"
          disabled={isLoading}
        />
        {errors.description && (
          <p className="form-error">
            <AlertCircle className="w-3.5 h-3.5" />
            {errors.description.message}
          </p>
        )}
      </motion.div>

      {/* 动态配置字段 */}
      <AnimatePresence mode="wait">
        {typeConfig && (
          <motion.div
            key={selectedType}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4"
          >
            <div className="border-t border-[var(--color-border)] pt-4">
              <h4 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">
                连接配置
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {typeConfig.fields.map((field, index) => (
                  <motion.div
                    key={field.name}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <label className="form-label">
                      {field.label}
                      {field.required && <span className="text-red-500">*</span>}
                    </label>
                    <input
                      {...register(`config.${field.name}`)}
                      type={field.type === 'password' ? 'password' : field.type === 'number' ? 'number' : 'text'}
                      placeholder={field.placeholder}
                      className="form-input"
                      disabled={isLoading}
                    />
                    {errors.config?.[field.name as keyof typeof errors.config] && (
                      <p className="form-error">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {String(errors.config[field.name as keyof typeof errors.config]?.message || '')}
                      </p>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>

            {/* 测试连接按钮 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <TestConnectionButton
                type={selectedType}
                config={testConfig || undefined}
                className="mt-4"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 操作按钮 */}
      <motion.div
        variants={itemVariants}
        className="flex items-center justify-end gap-3 pt-4 border-t border-[var(--color-border)]"
      >
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="
            px-5 py-2.5 rounded-lg
            text-[var(--color-text-secondary)]
            bg-white border border-[var(--color-border)]
            hover:bg-[var(--color-surface)]
            transition-all duration-200
            disabled:opacity-50
          "
        >
          取消
        </button>

        <motion.button
          type="submit"
          disabled={isLoading || !selectedType}
          whileHover={{ scale: isLoading ? 1 : 1.02 }}
          whileTap={{ scale: isLoading ? 1 : 0.98 }}
          className="
            px-5 py-2.5 rounded-lg
            text-white font-medium
            bg-gradient-to-r from-blue-600 to-blue-500
            hover:from-blue-700 hover:to-blue-600
            transition-all duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            shadow-md hover:shadow-lg
            flex items-center gap-2
          "
        >
          {isLoading ? (
            <>
              <Loader2 className="animate-spin w-4 h-4" />
              <span>保存中...</span>
            </>
          ) : (
            <span>{initialData ? '保存更改' : '创建连接器'}</span>
          )}
        </motion.button>
      </motion.div>
    </motion.form>
  );
}
