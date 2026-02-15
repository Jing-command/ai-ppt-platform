/**
 * 数据解析工具
 * @module lib/charts/dataParser
 * @description 提供Excel、CSV、JSON文件解析功能
 */

import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import type {
    ParsedData,
    DataSource,
    DataField,
    FieldDataType,
    FileType
} from '@/types/visualization';

// ============================================
// 工具函数
// ============================================

/**
 * 生成唯一ID
 * @returns 唯一标识字符串
 */
function generateId(): string {
    // 使用时间戳和随机数生成唯一ID
    return `ds_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * 获取文件扩展名
 * @param fileName - 文件名
 * @returns 文件扩展名（小写）
 */
function getFileExtension(fileName: string): string {
    // 获取最后一个点后的内容作为扩展名
    const lastDotIndex = fileName.lastIndexOf('.');
    if (lastDotIndex === -1) {
        return '';
    }
    return fileName.substring(lastDotIndex + 1).toLowerCase();
}

/**
 * 判断值的类型
 * @param value - 要判断的值
 * @returns 字段数据类型
 */
function getValueType(value: unknown): FieldDataType {
    // 空值判断
    if (value === null || value === undefined || value === '') {
        return 'string';
    }

    // 布尔类型判断
    if (typeof value === 'boolean') {
        return 'boolean';
    }

    // 数值类型判断
    if (typeof value === 'number' && !isNaN(value)) {
        return 'number';
    }

    // 日期类型判断
    if (value instanceof Date) {
        return 'date';
    }

    // 尝试解析日期字符串
    if (typeof value === 'string') {
        // ISO日期格式
        const isoDatePattern = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?/;
        if (isoDatePattern.test(value)) {
            const parsed = new Date(value);
            if (!isNaN(parsed.getTime())) {
                return 'date';
            }
        }

        // 常见日期格式
        const commonDatePattern = /^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}/;
        if (commonDatePattern.test(value)) {
            const parsed = new Date(value);
            if (!isNaN(parsed.getTime())) {
                return 'date';
            }
        }
    }

    // 对象类型判断
    if (typeof value === 'object') {
        return 'object';
    }

    // 默认返回字符串类型
    return 'string';
}

/**
 * 计算数值字段的统计信息
 * @param values - 数值数组
 * @returns 统计信息对象
 */
function calculateStats(values: number[]): {
    min: number;
    max: number;
    mean: number;
    median: number;
    sum: number;
} {
    // 过滤有效数值
    const validValues = values.filter(v => typeof v === 'number' && !isNaN(v));

    if (validValues.length === 0) {
        return {
            min: 0,
            max: 0,
            mean: 0,
            median: 0,
            sum: 0
        };
    }

    // 计算最小值
    const min = Math.min(...validValues);
    // 计算最大值
    const max = Math.max(...validValues);
    // 计算总和
    const sum = validValues.reduce((acc, val) => acc + val, 0);
    // 计算平均值
    const mean = sum / validValues.length;

    // 计算中位数
    const sorted = [...validValues].sort((a, b) => a - b);
    const midIndex = Math.floor(sorted.length / 2);
    const median = sorted.length % 2 !== 0
        ? sorted[midIndex]
        : (sorted[midIndex - 1] + sorted[midIndex]) / 2;

    return { min, max, mean, median, sum };
}

/**
 * 获取唯一值数量
 * @param values - 值数组
 * @returns 唯一值数量
 */
function getUniqueCount(values: unknown[]): number {
    // 使用Set计算唯一值
    const uniqueSet = new Set<string>();
    values.forEach(v => {
        if (v !== null && v !== undefined && v !== '') {
            uniqueSet.add(String(v));
        }
    });
    return uniqueSet.size;
}

/**
 * 获取示例值
 * @param values - 值数组
 * @param count - 示例数量
 * @returns 示例值数组
 */
function getSampleValues(values: unknown[], count: number = 5): unknown[] {
    // 获取前N个非空值作为示例
    const samples: unknown[] = [];
    for (let i = 0; i < values.length && samples.length < count; i++) {
        if (values[i] !== null && values[i] !== undefined && values[i] !== '') {
            samples.push(values[i]);
        }
    }
    return samples;
}

// ============================================
// 字段分析函数
// ============================================

/**
 * 分析数据字段
 * @param data - 数据数组
 * @returns 字段定义数组
 */
export function analyzeFields(data: unknown[]): DataField[] {
    // 空数据返回空数组
    if (!data || data.length === 0) {
        return [];
    }

    // 获取第一条数据作为字段模板
    const firstRow = data[0] as Record<string, unknown>;
    if (!firstRow || typeof firstRow !== 'object') {
        return [];
    }

    // 获取所有字段名
    const fieldNames = Object.keys(firstRow);
    const fields: DataField[] = [];

    // 遍历每个字段进行分析
    fieldNames.forEach((name, index) => {
        // 提取该字段的所有值
        const values = data.map(row => {
            const rowData = row as Record<string, unknown>;
            return rowData ? rowData[name] : undefined;
        });

        // 判断字段类型（基于前100行数据）
        const sampleSize = Math.min(100, values.length);
        const sampleValues = values.slice(0, sampleSize);
        let detectedType: FieldDataType = 'string';
        const typeCounts: Record<FieldDataType, number> = {
            string: 0,
            number: 0,
            boolean: 0,
            date: 0,
            object: 0
        };

        // 统计各类型出现次数
        sampleValues.forEach(v => {
            const t = getValueType(v);
            typeCounts[t]++;
        });

        // 选择出现次数最多的类型
        let maxCount = 0;
        Object.entries(typeCounts).forEach(([type, count]) => {
            if (count > maxCount) {
                maxCount = count;
                detectedType = type as FieldDataType;
            }
        });

        // 检查是否有空值
        const nullCount = values.filter(v => v === null || v === undefined || v === '').length;
        const nullable = nullCount > 0;

        // 计算唯一值数量
        const uniqueCount = getUniqueCount(values);

        // 获取示例值
        const samples = getSampleValues(values);

        // 构建字段定义
        const field: DataField = {
            name,
            type: detectedType,
            index,
            nullable,
            uniqueCount,
            sampleValues: samples
        };

        // 如果是数值类型，计算统计信息
        if (field.type === 'number') {
            const numericValues = values.filter(v => typeof v === 'number' && !isNaN(v)) as number[];
            field.stats = calculateStats(numericValues);
        }

        fields.push(field);
    });

    return fields;
}

// ============================================
// Excel解析函数
// ============================================

/**
 * 解析Excel文件
 * @param file - Excel文件对象
 * @returns 解析后的数据
 */
export async function parseExcel(file: File): Promise<ParsedData> {
    return new Promise((resolve, reject) => {
        // 创建文件读取器
        const reader = new FileReader();

        // 读取成功回调
        reader.onload = (event) => {
            try {
                // 获取文件数据
                const data = event.target?.result;
                if (!data) {
                    reject(new Error('文件读取失败'));
                    return;
                }

                // 解析工作簿
                const workbook = XLSX.read(data, { type: 'array' });

                // 获取第一个工作表名称
                const firstSheetName = workbook.SheetNames[0];
                if (!firstSheetName) {
                    reject(new Error('Excel文件中没有工作表'));
                    return;
                }

                // 获取工作表
                const worksheet = workbook.Sheets[firstSheetName];

                // 转换为JSON数组
                const jsonData = XLSX.utils.sheet_to_json(worksheet, {
                    defval: null,
                    raw: false
                });

                // 创建数据源信息
                const source: DataSource = {
                    id: generateId(),
                    name: file.name.replace(/\.[^/.]+$/, ''),
                    type: 'file',
                    fileType: getFileExtension(file.name) as FileType,
                    fileSize: file.size,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                    originalFileName: file.name
                };

                // 分析字段
                const fields = analyzeFields(jsonData);

                // 返回解析结果
                resolve({
                    source,
                    fields,
                    rows: jsonData as Record<string, unknown>[],
                    totalRows: jsonData.length,
                    parsedAt: new Date()
                });
            } catch (error) {
                // 解析错误处理
                reject(new Error(`Excel解析失败: ${error instanceof Error ? error.message : '未知错误'}`));
            }
        };

        // 读取失败回调
        reader.onerror = () => {
            reject(new Error('文件读取失败'));
        };

        // 开始读取文件（ArrayBuffer格式）
        reader.readAsArrayBuffer(file);
    });
}

// ============================================
// CSV解析函数
// ============================================

/**
 * 解析CSV文件
 * @param file - CSV文件对象
 * @returns 解析后的数据
 */
export async function parseCSV(file: File): Promise<ParsedData> {
    return new Promise((resolve, reject) => {
        // 使用PapaParse解析CSV
        Papa.parse(file, {
            // 解析完成回调
            complete: (results) => {
                try {
                    // 检查解析错误
                    if (results.errors.length > 0) {
                        const errorMessages = results.errors.map(e => e.message).join('; ');
                        reject(new Error(`CSV解析错误: ${errorMessages}`));
                        return;
                    }

                    // 获取数据
                    const data = results.data as unknown[][];

                    // 检查数据有效性
                    if (!data || data.length < 2) {
                        reject(new Error('CSV文件数据不足'));
                        return;
                    }

                    // 第一行作为表头
                    const headers = data[0] as string[];
                    if (!headers || headers.length === 0) {
                        reject(new Error('CSV文件没有有效的表头'));
                        return;
                    }

                    // 转换为对象数组
                    const jsonData: Record<string, unknown>[] = [];
                    for (let i = 1; i < data.length; i++) {
                        const row = data[i] as unknown[];
                        // 跳过空行
                        if (!row || row.every(cell => cell === null || cell === undefined || cell === '')) {
                            continue;
                        }

                        // 构建行对象
                        const rowObj: Record<string, unknown> = {};
                        headers.forEach((header, index) => {
                            // 使用表头作为键，对应单元格作为值
                            rowObj[header] = row[index];
                        });
                        jsonData.push(rowObj);
                    }

                    // 创建数据源信息
                    const source: DataSource = {
                        id: generateId(),
                        name: file.name.replace(/\.[^/.]+$/, ''),
                        type: 'file',
                        fileType: 'csv',
                        fileSize: file.size,
                        createdAt: new Date(),
                        updatedAt: new Date(),
                        originalFileName: file.name
                    };

                    // 分析字段
                    const fields = analyzeFields(jsonData);

                    // 返回解析结果
                    resolve({
                        source,
                        fields,
                        rows: jsonData,
                        totalRows: jsonData.length,
                        parsedAt: new Date()
                    });
                } catch (error) {
                    // 解析错误处理
                    reject(new Error(`CSV解析失败: ${error instanceof Error ? error.message : '未知错误'}`));
                }
            },
            // 解析错误回调
            error: (error) => {
                reject(new Error(`CSV解析失败: ${error.message}`));
            },
            // 解析配置
            header: false,
            skipEmptyLines: true,
            encoding: 'UTF-8'
        });
    });
}

// ============================================
// JSON解析函数
// ============================================

/**
 * 解析JSON文件
 * @param file - JSON文件对象
 * @returns 解析后的数据
 */
export async function parseJSON(file: File): Promise<ParsedData> {
    return new Promise((resolve, reject) => {
        // 创建文件读取器
        const reader = new FileReader();

        // 读取成功回调
        reader.onload = (event) => {
            try {
                // 获取文件内容
                const content = event.target?.result as string;
                if (!content) {
                    reject(new Error('文件读取失败'));
                    return;
                }

                // 解析JSON
                const parsed = JSON.parse(content);

                // 确保数据是数组格式
                let jsonData: unknown[] = [];
                if (Array.isArray(parsed)) {
                    jsonData = parsed;
                } else if (typeof parsed === 'object' && parsed !== null) {
                    // 如果是对象，尝试提取数据数组
                    const possibleArrayFields = ['data', 'items', 'records', 'rows', 'results'];
                    let found = false;
                    for (const field of possibleArrayFields) {
                        if (Array.isArray((parsed as Record<string, unknown>)[field])) {
                            jsonData = (parsed as Record<string, unknown>)[field] as unknown[];
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        // 将单个对象包装为数组
                        jsonData = [parsed];
                    }
                } else {
                    reject(new Error('JSON格式不正确，需要对象或数组格式'));
                    return;
                }

                // 检查数据有效性
                if (!jsonData || jsonData.length === 0) {
                    reject(new Error('JSON文件没有数据'));
                    return;
                }

                // 创建数据源信息
                const source: DataSource = {
                    id: generateId(),
                    name: file.name.replace(/\.[^/.]+$/, ''),
                    type: 'file',
                    fileType: 'json',
                    fileSize: file.size,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                    originalFileName: file.name
                };

                // 分析字段
                const fields = analyzeFields(jsonData);

                // 返回解析结果
                resolve({
                    source,
                    fields,
                    rows: jsonData as Record<string, unknown>[],
                    totalRows: jsonData.length,
                    parsedAt: new Date()
                });
            } catch (error) {
                // 解析错误处理
                if (error instanceof SyntaxError) {
                    reject(new Error('JSON格式错误，请检查文件内容'));
                } else {
                    reject(new Error(`JSON解析失败: ${error instanceof Error ? error.message : '未知错误'}`));
                }
            }
        };

        // 读取失败回调
        reader.onerror = () => {
            reject(new Error('文件读取失败'));
        };

        // 开始读取文件（文本格式）
        reader.readAsText(file, 'UTF-8');
    });
}

// ============================================
// 统一解析函数
// ============================================

/**
 * 根据文件类型自动选择解析器
 * @param file - 文件对象
 * @returns 解析后的数据
 */
export async function parseFile(file: File): Promise<ParsedData> {
    // 获取文件扩展名
    const extension = getFileExtension(file.name);

    // 根据扩展名选择解析器
    switch (extension) {
        case 'xlsx':
        case 'xls':
            return parseExcel(file);
        case 'csv':
            return parseCSV(file);
        case 'json':
            return parseJSON(file);
        default:
            throw new Error(`不支持的文件格式: ${extension}`);
    }
}

/**
 * 验证文件是否可解析
 * @param file - 文件对象
 * @returns 是否可解析及错误信息
 */
export function validateFile(file: File): { valid: boolean; error?: string } {
    // 获取文件扩展名
    const extension = getFileExtension(file.name);

    // 检查文件类型
    const supportedTypes = ['xlsx', 'xls', 'csv', 'json'];
    if (!supportedTypes.includes(extension)) {
        return {
            valid: false,
            error: `不支持的文件格式，支持: ${supportedTypes.join(', ')}`
        };
    }

    // 检查文件大小（限制50MB）
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        return {
            valid: false,
            error: '文件大小超过限制（最大50MB）'
        };
    }

    // 检查文件是否为空
    if (file.size === 0) {
        return {
            valid: false,
            error: '文件为空'
        };
    }

    return { valid: true };
}
