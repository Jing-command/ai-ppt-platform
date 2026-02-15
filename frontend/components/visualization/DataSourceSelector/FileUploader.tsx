// components/visualization/DataSourceSelector/FileUploader.tsx
// 文件上传组件 - 支持拖拽上传和解析数据文件

'use client';

import {useState, useCallback, useRef} from 'react';
import {motion, AnimatePresence} from 'framer-motion';
import {
    Upload,
    FileSpreadsheet,
    FileJson,
    FileText,
    CheckCircle,
    AlertCircle,
    Loader2
} from 'lucide-react';
import * as XLSX from 'xlsx';
import type {
    ParsedData,
    DataSource,
    DataField,
    FileType,
    FieldDataType
} from '@/types/visualization';

/**
 * 文件类型配置
 */
interface FileTypeConfig {
    /** 文件扩展名 */
    extensions: string[];
    /** MIME 类型 */
    mimeTypes: string[];
    /** 图标 */
    icon: React.ReactNode;
    /** 显示名称 */
    label: string;
}

/**
 * 支持的文件类型配置映射
 */
const FILE_TYPE_CONFIGS: Record<FileType, FileTypeConfig> = {
    xlsx: {
        extensions: ['.xlsx'],
        mimeTypes: [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        icon: <FileSpreadsheet className="w-8 h-8 text-green-500" />,
        label: 'Excel 2007+'
    },
    xls: {
        extensions: ['.xls'],
        mimeTypes: ['application/vnd.ms-excel'],
        icon: <FileSpreadsheet className="w-8 h-8 text-green-600" />,
        label: 'Excel 97-2003'
    },
    csv: {
        extensions: ['.csv'],
        mimeTypes: ['text/csv'],
        icon: <FileText className="w-8 h-8 text-blue-500" />,
        label: 'CSV'
    },
    json: {
        extensions: ['.json'],
        mimeTypes: ['application/json'],
        icon: <FileJson className="w-8 h-8 text-orange-500" />,
        label: 'JSON'
    }
};

/**
 * 上传状态枚举
 */
type UploadStatus = 'idle' | 'dragging' | 'uploading' | 'parsing' | 'success' | 'error';

/**
 * FileUploader 组件属性
 */
interface FileUploaderProps {
    /** 文件上传成功回调 */
    onUpload: (data: ParsedData) => void;
}

/**
 * 文件上传组件
 * 支持拖拽上传 Excel、CSV、JSON 文件，并解析数据
 */
export default function FileUploader({onUpload}: FileUploaderProps) {
    // 上传状态
    const [status, setStatus] = useState<UploadStatus>('idle');
    // 错误信息
    const [error, setError] = useState<string | null>(null);
    // 上传进度
    const [progress, setProgress] = useState(0);
    // 当前文件信息
    const [currentFile, setCurrentFile] = useState<File | null>(null);
    // 文件输入框引用
    const fileInputRef = useRef<HTMLInputElement>(null);

    /**
     * 根据文件名获取文件类型
     * @param fileName - 文件名
     * @returns 文件类型或 null
     */
    const getFileType = (fileName: string): FileType | null => {
        // 转换为小写并获取扩展名
        const ext = fileName.toLowerCase().slice(fileName.lastIndexOf('.'));

        // 遍历文件类型配置查找匹配
        for (const [type, config] of Object.entries(FILE_TYPE_CONFIGS)) {
            if (config.extensions.includes(ext)) {
                return type as FileType;
            }
        }

        return null;
    };

    /**
     * 推断字段数据类型
     * @param values - 字段值数组
     * @returns 推断的数据类型
     */
    const inferFieldType = (values: unknown[]): FieldDataType => {
        // 过滤非空值
        const nonNullValues = values.filter(v => v !== null && v !== undefined && v !== '');

        if (nonNullValues.length === 0) {
            return 'string';
        }

        // 检查是否为布尔值
        const isBoolean = nonNullValues.every(v =>
            typeof v === 'boolean' || v === 'true' || v === 'false'
        );
        if (isBoolean) {
            return 'boolean';
        }

        // 检查是否为数值
        const isNumber = nonNullValues.every(v =>
            typeof v === 'number' || (!isNaN(Number(v)) && v !== '')
        );
        if (isNumber) {
            return 'number';
        }

        // 检查是否为日期
        const isDate = nonNullValues.every(v => {
            if (v instanceof Date) {
                return true;
            }
            const date = new Date(v as string);
            return !isNaN(date.getTime());
        });
        if (isDate) {
            return 'date';
        }

        // 检查是否为对象
        const isObject = nonNullValues.every(v =>
            typeof v === 'object' && !Array.isArray(v)
        );
        if (isObject) {
            return 'object';
        }

        return 'string';
    };

    /**
     * 计算字段的统计信息
     * @param values - 数值数组
     * @returns 统计信息对象
     */
    const calculateStats = (values: number[]) => {
        // 过滤有效数值
        const validValues = values.filter(v => !isNaN(v) && isFinite(v));
        const n = validValues.length;

        if (n === 0) {
            return undefined;
        }

        // 排序用于计算中位数
        const sorted = [...validValues].sort((a, b) => a - b);

        // 计算各项统计值
        const sum = validValues.reduce((acc, val) => acc + val, 0);
        const mean = sum / n;
        const median = n % 2 === 0
            ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2
            : sorted[Math.floor(n / 2)];

        return {
            min: sorted[0],
            max: sorted[n - 1],
            mean: Math.round(mean * 100) / 100,
            median,
            sum: Math.round(sum * 100) / 100
        };
    };

    /**
     * 解析数据字段信息
     * @param rows - 数据行数组
     * @returns 字段定义数组
     */
    const parseFields = (rows: Record<string, unknown>[]): DataField[] => {
        if (rows.length === 0) {
            return [];
        }

        // 获取所有字段名
        const fieldNames = Object.keys(rows[0]);

        return fieldNames.map((name, index) => {
            // 提取该字段的所有值
            const values = rows.map(row => row[name]);
            const type = inferFieldType(values);

            // 计算唯一值数量
            const uniqueValues = new Set(values.filter(v =>
                v !== null && v !== undefined && v !== ''
            ));

            // 获取示例值
            const sampleValues = values
                .filter(v => v !== null && v !== undefined && v !== '')
                .slice(0, 5);

            // 数值类型计算统计信息
            let stats;
            if (type === 'number') {
                const numValues = values
                    .map(v => typeof v === 'number' ? v : Number(v))
                    .filter(v => !isNaN(v));
                stats = calculateStats(numValues);
            }

            return {
                name,
                type,
                index,
                nullable: values.some(v => v === null || v === undefined || v === ''),
                uniqueCount: uniqueValues.size,
                sampleValues,
                stats
            };
        });
    };

    /**
     * 解析 Excel 文件
     * @param arrayBuffer - 文件 ArrayBuffer
     * @returns 数据行数组
     */
    const parseExcel = (arrayBuffer: ArrayBuffer): Record<string, unknown>[] => {
        // 读取工作簿
        const workbook = XLSX.read(arrayBuffer, {type: 'array'});
        // 获取第一个工作表名称
        const sheetName = workbook.SheetNames[0];
        // 获取工作表
        const worksheet = workbook.Sheets[sheetName];
        // 转换为 JSON 格式
        return XLSX.utils.sheet_to_json(worksheet);
    };

    /**
     * 解析 CSV 文件
     * @param text - 文件文本内容
     * @returns 数据行数组
     */
    const parseCSV = (text: string): Record<string, unknown>[] => {
        // 使用 XLSX 解析 CSV
        const workbook = XLSX.read(text, {type: 'string'});
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        return XLSX.utils.sheet_to_json(worksheet);
    };

    /**
     * 解析 JSON 文件
     * @param text - 文件文本内容
     * @returns 数据行数组
     */
    const parseJSON = (text: string): Record<string, unknown>[] => {
        const data = JSON.parse(text);
        // 如果是数组直接返回，否则包装成数组
        return Array.isArray(data) ? data : [data];
    };

    /**
     * 处理文件上传
     * @param file - 上传的文件
     */
    const handleFileUpload = async (file: File) => {
        // 重置状态
        setError(null);
        setProgress(0);
        setCurrentFile(file);

        // 验证文件类型
        const fileType = getFileType(file.name);
        if (!fileType) {
            setStatus('error');
            setError('不支持的文件格式，请上传 Excel、CSV 或 JSON 文件');
            return;
        }

        setStatus('uploading');

        try {
            // 模拟上传进度
            setProgress(30);

            // 读取文件内容
            let rows: Record<string, unknown>[];

            if (fileType === 'xlsx' || fileType === 'xls') {
                // Excel 文件使用 ArrayBuffer 读取
                const arrayBuffer = await file.arrayBuffer();
                setStatus('parsing');
                setProgress(50);
                rows = parseExcel(arrayBuffer);
            } else if (fileType === 'csv') {
                // CSV 文件使用文本读取
                const text = await file.text();
                setStatus('parsing');
                setProgress(50);
                rows = parseCSV(text);
            } else {
                // JSON 文件使用文本读取
                const text = await file.text();
                setStatus('parsing');
                setProgress(50);
                rows = parseJSON(text);
            }

            setProgress(80);

            // 解析字段信息
            const fields = parseFields(rows);

            setProgress(100);

            // 创建数据源信息
            const dataSource: DataSource = {
                id: `ds_${Date.now()}`,
                name: file.name,
                type: 'file',
                fileType,
                fileSize: file.size,
                createdAt: new Date(),
                updatedAt: new Date(),
                originalFileName: file.name
            };

            // 创建解析后的数据对象
            const parsedData: ParsedData = {
                source: dataSource,
                fields,
                rows,
                totalRows: rows.length,
                parsedAt: new Date()
            };

            setStatus('success');

            // 回调通知父组件
            setTimeout(() => {
                onUpload(parsedData);
            }, 500);
        } catch (err) {
            setStatus('error');
            setError(err instanceof Error ? err.message : '文件解析失败，请检查文件格式');
        }
    };

    /**
     * 处理拖拽进入
     */
    const handleDragEnter = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setStatus('dragging');
    }, []);

    /**
     * 处理拖拽离开
     */
    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setStatus('idle');
    }, []);

    /**
     * 处理拖拽悬停
     */
    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    /**
     * 处理文件放下
     */
    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // eslint-disable-next-line @typescript-eslint/no-use-before-define
            handleFileUpload(files[0]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    /**
     * 处理文件选择
     */
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    /**
     * 触发文件选择
     */
    const triggerFileSelect = () => {
        fileInputRef.current?.click();
    };

    /**
     * 重置上传状态
     */
    const handleReset = () => {
        setStatus('idle');
        setError(null);
        setProgress(0);
        setCurrentFile(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    /**
     * 格式化文件大小
     */
    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) {
            return `${bytes} B`;
        }
        if (bytes < 1024 * 1024) {
            return `${(bytes / 1024).toFixed(1)} KB`;
        }
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="w-full">
            {/* 隐藏的文件输入框 */}
            <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv,.json"
                onChange={handleFileSelect}
                className="hidden"
            />

            {/* 上传区域 */}
            <motion.div
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={status === 'idle' ? triggerFileSelect : undefined}
                // 上传区域动画：根据状态变化
                animate={{
                    borderColor: status === 'dragging' ? '#3b82f6' : '#e5e7eb',
                    backgroundColor: status === 'dragging' ? '#eff6ff' : '#fafafa'
                }}
                className={`
                    relative p-8 rounded-xl border-2 border-dashed
                    transition-colors duration-100
                    ${status === 'idle' ? 'cursor-pointer hover:border-blue-400 hover:bg-blue-50' : ''}
                `}
            >
                <AnimatePresence mode="wait">
                    {/* 空闲状态 */}
                    {status === 'idle' && (
                        <motion.div
                            key="idle"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center text-center"
                        >
                            {/* 上传图标 */}
                            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-4">
                                <Upload className="w-8 h-8 text-blue-500" />
                            </div>

                            {/* 提示文字 */}
                            <p className="text-sm font-medium text-gray-700 mb-1">
                                拖拽文件到此处，或点击上传
                            </p>
                            <p className="text-xs text-gray-500 mb-4">
                                支持 Excel (.xlsx, .xls)、CSV、JSON 格式
                            </p>

                            {/* 支持的文件类型图标 */}
                            <div className="flex items-center gap-3">
                                {Object.entries(FILE_TYPE_CONFIGS).map(([type, config]) => (
                                    <div
                                        key={type}
                                        className="flex flex-col items-center"
                                    >
                                        {config.icon}
                                        <span className="text-[10px] text-gray-400 mt-1">
                                            {config.label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* 上传中状态 */}
                    {(status === 'uploading' || status === 'parsing') && (
                        <motion.div
                            key="uploading"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center text-center"
                        >
                            {/* 加载图标 */}
                            <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />

                            {/* 状态文字 */}
                            <p className="text-sm font-medium text-gray-700 mb-2">
                                {status === 'uploading' ? '正在上传...' : '正在解析数据...'}
                            </p>

                            {/* 进度条 */}
                            <div className="w-full max-w-xs h-2 bg-gray-200 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-blue-500"
                                    initial={{width: 0}}
                                    animate={{width: `${progress}%`}}
                                    transition={{duration: 0.1}}
                                />
                            </div>

                            {/* 文件名 */}
                            {currentFile && (
                                <p className="text-xs text-gray-500 mt-2">
                                    {currentFile.name}
                                </p>
                            )}
                        </motion.div>
                    )}

                    {/* 成功状态 */}
                    {status === 'success' && (
                        <motion.div
                            key="success"
                            initial={{opacity: 0, scale: 0.9}}
                            animate={{opacity: 1, scale: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center text-center"
                        >
                            {/* 成功图标 */}
                            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
                                <CheckCircle className="w-10 h-10 text-green-500" />
                            </div>

                            {/* 成功文字 */}
                            <p className="text-sm font-medium text-green-600 mb-1">
                                文件解析成功
                            </p>

                            {/* 文件信息 */}
                            {currentFile && (
                                <p className="text-xs text-gray-500">
                                    {currentFile.name} ({formatFileSize(currentFile.size)})
                                </p>
                            )}
                        </motion.div>
                    )}

                    {/* 错误状态 */}
                    {status === 'error' && (
                        <motion.div
                            key="error"
                            initial={{opacity: 0}}
                            animate={{opacity: 1}}
                            exit={{opacity: 0}}
                            className="flex flex-col items-center text-center"
                        >
                            {/* 错误图标 */}
                            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mb-4">
                                <AlertCircle className="w-10 h-10 text-red-500" />
                            </div>

                            {/* 错误文字 */}
                            <p className="text-sm font-medium text-red-600 mb-1">
                                上传失败
                            </p>

                            {/* 错误信息 */}
                            <p className="text-xs text-gray-500 mb-4">
                                {error}
                            </p>

                            {/* 重试按钮 */}
                            <motion.button
                                onClick={handleReset}
                                whileHover={{scale: 1.02}}
                                whileTap={{scale: 0.98}}
                                className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                            >
                                重新上传
                            </motion.button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}
