// components/visualization/DataSourceSelector/index.tsx
// 数据源选择器主组件 - 提供文件上传和数据库连接两种数据源选择

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Database, ArrowRight } from 'lucide-react';
import type { DataSource, ParsedData } from '@/types/visualization';
import FileUploader from './FileUploader';

/**
 * 数据源类型选项
 */
type DataSourceOption = 'file' | 'database';

/**
 * DataSourceSelector 组件属性
 */
interface DataSourceSelectorProps {
    /** 数据源选择回调 */
    onSelect: (dataSource: DataSource) => void;
    /** 文件上传成功回调（包含解析后的数据） */
    onFileParsed?: (data: ParsedData) => void;
}

/**
 * 数据源选择器主组件
 * 提供文件上传和数据库连接两种数据源选择方式
 */
export default function DataSourceSelector({
    onSelect,
    onFileParsed
}: DataSourceSelectorProps) {
    // 当前选中的数据源类型
    const [selectedOption, setSelectedOption] = useState<DataSourceOption | null>(null);

    /**
     * 处理文件上传成功
     * @param data - 解析后的数据
     */
    const handleFileUpload = (data: ParsedData) => {
        // 通知父组件数据源已选择
        onSelect(data.source);
        // 如果提供了文件解析回调，也通知父组件
        if (onFileParsed) {
            onFileParsed(data);
        }
    };

    /**
     * 处理数据库连接选择
     * TODO: 实现数据库连接功能
     */
    const handleDatabaseConnect = () => {
        // 创建模拟数据源
        const dataSource: DataSource = {
            id: `ds_db_${Date.now()}`,
            name: '数据库连接',
            type: 'database',
            createdAt: new Date(),
            updatedAt: new Date()
        };
        onSelect(dataSource);
    };

    /**
     * 返回选择界面
     */
    const handleBack = () => {
        setSelectedOption(null);
    };

    return (
        <div className="w-full">
            <AnimatePresence mode="wait">
                {/* 数据源类型选择界面 */}
                {!selectedOption && (
                    <motion.div
                        key="options"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.1 }}
                        className="grid grid-cols-1 md:grid-cols-2 gap-4"
                    >
                        {/* 文件上传选项 */}
                        <motion.button
                            onClick={() => setSelectedOption('file')}
                            // 按钮动画：悬停上浮
                            whileHover={{ y: -4, scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            transition={{ duration: 0.1 }}
                            className="
                                p-6 rounded-xl border-2 border-gray-200 bg-white
                                hover:border-blue-400 hover:bg-blue-50
                                transition-colors duration-100
                                text-left
                            "
                        >
                            {/* 图标 */}
                            <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center mb-4">
                                <Upload className="w-7 h-7 text-blue-500" />
                            </div>

                            {/* 标题 */}
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">
                                文件上传
                            </h3>

                            {/* 描述 */}
                            <p className="text-sm text-gray-500 mb-4">
                                上传 Excel、CSV 或 JSON 文件，自动解析数据结构
                            </p>

                            {/* 支持格式标签 */}
                            <div className="flex flex-wrap gap-2">
                                <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-600">
                                    Excel
                                </span>
                                <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-600">
                                    CSV
                                </span>
                                <span className="px-2 py-1 text-xs rounded bg-orange-100 text-orange-600">
                                    JSON
                                </span>
                            </div>

                            {/* 选择指示器 */}
                            <div className="flex items-center justify-end mt-4 text-blue-500">
                                <span className="text-sm font-medium">选择</span>
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </div>
                        </motion.button>

                        {/* 数据库连接选项 */}
                        <motion.button
                            onClick={() => setSelectedOption('database')}
                            // 按钮动画：悬停上浮
                            whileHover={{ y: -4, scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            transition={{ duration: 0.1 }}
                            className="
                                p-6 rounded-xl border-2 border-gray-200 bg-white
                                hover:border-purple-400 hover:bg-purple-50
                                transition-colors duration-100
                                text-left
                            "
                        >
                            {/* 图标 */}
                            <div className="w-14 h-14 rounded-xl bg-purple-100 flex items-center justify-center mb-4">
                                <Database className="w-7 h-7 text-purple-500" />
                            </div>

                            {/* 标题 */}
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">
                                数据库连接
                            </h3>

                            {/* 描述 */}
                            <p className="text-sm text-gray-500 mb-4">
                                连接 MySQL、PostgreSQL 等数据库，直接读取数据
                            </p>

                            {/* 支持数据库标签 */}
                            <div className="flex flex-wrap gap-2">
                                <span className="px-2 py-1 text-xs rounded bg-indigo-100 text-indigo-600">
                                    MySQL
                                </span>
                                <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-600">
                                    PostgreSQL
                                </span>
                                <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-600">
                                    MongoDB
                                </span>
                            </div>

                            {/* 选择指示器 */}
                            <div className="flex items-center justify-end mt-4 text-purple-500">
                                <span className="text-sm font-medium">选择</span>
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </div>

                            {/* 开发中提示 */}
                            <div className="mt-2 px-2 py-1 text-xs rounded bg-gray-100 text-gray-500 inline-block">
                                即将推出
                            </div>
                        </motion.button>
                    </motion.div>
                )}

                {/* 文件上传界面 */}
                {selectedOption === 'file' && (
                    <motion.div
                        key="file-upload"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.1 }}
                    >
                        {/* 返回按钮 */}
                        <motion.button
                            onClick={handleBack}
                            // 返回按钮动画：悬停效果
                            whileHover={{ x: -2 }}
                            className="
                                flex items-center gap-1 mb-4
                                text-sm text-gray-500 hover:text-gray-700
                                transition-colors
                            "
                        >
                            <ArrowRight className="w-4 h-4 rotate-180" />
                            <span>返回选择</span>
                        </motion.button>

                        {/* 文件上传组件 */}
                        <FileUploader onUpload={handleFileUpload} />
                    </motion.div>
                )}

                {/* 数据库连接界面 */}
                {selectedOption === 'database' && (
                    <motion.div
                        key="database-connect"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.1 }}
                    >
                        {/* 返回按钮 */}
                        <motion.button
                            onClick={handleBack}
                            whileHover={{ x: -2 }}
                            className="
                                flex items-center gap-1 mb-4
                                text-sm text-gray-500 hover:text-gray-700
                                transition-colors
                            "
                        >
                            <ArrowRight className="w-4 h-4 rotate-180" />
                            <span>返回选择</span>
                        </motion.button>

                        {/* 开发中提示 */}
                        <div className="p-8 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 text-center">
                            <Database className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500 mb-2">数据库连接功能开发中</p>
                            <p className="text-sm text-gray-400">
                                请暂时使用文件上传功能
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
