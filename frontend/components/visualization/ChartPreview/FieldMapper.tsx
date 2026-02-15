// components/visualization/ChartPreview/FieldMapper.tsx
// 字段映射组件 - 用于配置数据字段与图表维度的映射关系

'use client';

import { motion } from 'framer-motion';
import {
    ArrowDown,
    Hash,
    Type,
    Calendar,
    ToggleLeft,
    Layers
} from 'lucide-react';
import type { DataField, ChartFieldMapping, FieldDataType } from '@/types/visualization';

/**
 * 字段类型图标映射
 */
const FIELD_TYPE_ICONS: Record<FieldDataType, React.ReactNode> = {
    string: <Type className="w-4 h-4" />,
    number: <Hash className="w-4 h-4" />,
    boolean: <ToggleLeft className="w-4 h-4" />,
    date: <Calendar className="w-4 h-4" />,
    object: <Layers className="w-4 h-4" />
};

/**
 * 字段类型颜色映射
 */
const FIELD_TYPE_COLORS: Record<FieldDataType, string> = {
    string: 'text-blue-500 bg-blue-50',
    number: 'text-green-500 bg-green-50',
    boolean: 'text-purple-500 bg-purple-50',
    date: 'text-orange-500 bg-orange-50',
    object: 'text-gray-500 bg-gray-50'
};

/**
 * FieldMapper 组件属性
 */
interface FieldMapperProps {
    /** 可用字段列表 */
    fields: DataField[];
    /** 当前字段映射配置 */
    mapping: ChartFieldMapping;
    /** 映射变更回调 */
    onChange: (mapping: ChartFieldMapping) => void;
}

/**
 * 字段映射组件
 * 提供维度字段选择和度量字段多选功能
 */
export default function FieldMapper({
    fields,
    mapping,
    onChange
}: FieldMapperProps) {
    /**
     * 处理维度字段变更
     */
    const handleDimensionChange = (fieldName: string) => {
        onChange({
            ...mapping,
            dimension: fieldName || undefined
        });
    };

    /**
     * 处理度量字段变更（多选）
     */
    const handleMeasureChange = (fieldName: string, checked: boolean) => {
        let newMeasures: string[];

        if (checked) {
            // 添加度量字段
            newMeasures = [...mapping.measures, fieldName];
        } else {
            // 移除度量字段
            newMeasures = mapping.measures.filter(m => m !== fieldName);
        }

        onChange({
            ...mapping,
            measures: newMeasures
        });
    };

    /**
     * 处理颜色字段变更
     */
    const handleColorFieldChange = (fieldName: string) => {
        onChange({
            ...mapping,
            colorField: fieldName || undefined
        });
    };

    /**
     * 渲染字段选择下拉框
     */
    const renderFieldSelect = (
        label: string,
        value: string | undefined,
        onChange: (value: string) => void,
        placeholder: string,
        allowEmpty: boolean = true,
        id: string = ''
    ) => {
        // 生成唯一 ID
        const selectId = id || `select-${label.replace(/\s+/g, '-').toLowerCase()}`;

        return (
            <div className="space-y-1.5">
                {/* 标签 */}
                <label htmlFor={selectId} className="text-sm font-medium text-gray-700">
                    {label}
                </label>

                {/* 下拉框 */}
                <select
                    id={selectId}
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    className="
                        w-full px-3 py-2 text-sm rounded-lg
                        border border-gray-200 bg-white
                        focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
                    "
                >
                    {/* 空选项 */}
                    {allowEmpty && (
                        <option value="">{placeholder}</option>
                    )}

                    {/* 字段选项 */}
                    {fields.map((field) => (
                        <option key={field.name} value={field.name}>
                            {field.name}
                        </option>
                    ))}
                </select>
            </div>
        );
    };

    /**
     * 渲染度量字段多选列表
     */
    const renderMeasureCheckboxes = () => {
        // 筛选数值类型字段作为度量
        const numericFields = fields.filter(f => f.type === 'number');

        return (
            <div className="space-y-1.5">
                {/* 标签 */}
                <label className="text-sm font-medium text-gray-700">
                    度量字段（数值）
                </label>

                {/* 字段列表 */}
                <div className="space-y-1.5 max-h-40 overflow-y-auto p-2 rounded-lg border border-gray-200 bg-gray-50">
                    {numericFields.length === 0 ? (
                        <p className="text-sm text-gray-400 text-center py-2">
                            暂无数值字段
                        </p>
                    ) : (
                        numericFields.map((field) => {
                            const isChecked = mapping.measures.includes(field.name);

                            return (
                                <motion.label
                                    key={field.name}
                                    // 复选框动画：悬停效果
                                    whileHover={{ scale: 1.01 }}
                                    className={`
                                        flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
                                        transition-colors duration-100
                                        ${isChecked
                                            ? 'bg-blue-100 border border-blue-200'
                                            : 'bg-white border border-gray-200 hover:bg-gray-100'
                                        }
                                    `}
                                >
                                    {/* 复选框 */}
                                    <input
                                        type="checkbox"
                                        checked={isChecked}
                                        onChange={(e) => handleMeasureChange(field.name, e.target.checked)}
                                        className="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                                    />

                                    {/* 字段类型图标 */}
                                    <span className={`p-1 rounded ${FIELD_TYPE_COLORS[field.type]}`}>
                                        {FIELD_TYPE_ICONS[field.type]}
                                    </span>

                                    {/* 字段名称 */}
                                    <span className="text-sm text-gray-700 flex-1">
                                        {field.name}
                                    </span>

                                    {/* 统计信息 */}
                                    {field.stats && (
                                        <span className="text-xs text-gray-400">
                                            范围: {field.stats.min} - {field.stats.max}
                                        </span>
                                    )}
                                </motion.label>
                            );
                        })
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-4">
            {/* 标题 */}
            <div className="flex items-center gap-2 text-sm font-medium text-gray-800">
                <ArrowDown className="w-4 h-4 text-blue-500" />
                <span>字段映射配置</span>
            </div>

            {/* 维度字段选择 */}
            {renderFieldSelect(
                '维度字段（X轴）',
                mapping.dimension,
                handleDimensionChange,
                '选择维度字段...'
            )}

            {/* 度量字段多选 */}
            {renderMeasureCheckboxes()}

            {/* 颜色分组字段选择 */}
            {renderFieldSelect(
                '颜色分组字段（可选）',
                mapping.colorField,
                handleColorFieldChange,
                '选择分组字段...'
            )}

            {/* 当前映射状态 */}
            <div className="pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500 mb-2">当前映射:</p>
                <div className="flex flex-wrap gap-1.5">
                    {mapping.dimension && (
                        <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-600">
                            维度: {mapping.dimension}
                        </span>
                    )}
                    {mapping.measures.map((measure) => (
                        <span key={measure} className="px-2 py-1 text-xs rounded bg-green-100 text-green-600">
                            度量: {measure}
                        </span>
                    ))}
                    {mapping.colorField && (
                        <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-600">
                            分组: {mapping.colorField}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
