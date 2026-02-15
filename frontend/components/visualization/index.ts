// components/visualization/index.ts
// 数据可视化组件导出索引

// ============================================
// 图表选择器组件
// ============================================
export { default as ChartSelector } from './ChartSelector';
export { default as CategoryTabs } from './ChartSelector/CategoryTabs';
export { default as ChartCard } from './ChartSelector/ChartCard';
export { CHART_CONFIGS } from './ChartSelector';

// ============================================
// 数据源选择器组件
// ============================================
export { default as DataSourceSelector } from './DataSourceSelector';
export { default as FileUploader } from './DataSourceSelector/FileUploader';

// ============================================
// 图表预览组件
// ============================================
export { default as ChartPreview } from './ChartPreview';
export { default as EChartsRenderer } from './ChartPreview/EChartsRenderer';
export { default as FieldMapper } from './ChartPreview/FieldMapper';
export { default as StyleEditor } from './ChartPreview/StyleEditor';

// ============================================
// AI 推荐组件
// ============================================
export { default as AIRecommend } from './AIRecommend';
export { default as RecommendCard } from './AIRecommend/RecommendCard';
export type { RecommendedChart } from './AIRecommend/RecommendCard';

// ============================================
// 暂存图表组件
// ============================================
export { default as StoredCharts } from './StoredCharts';
export { default as StoredChartCard } from './StoredCharts/StoredChartCard';

// ============================================
// 类型重导出
// ============================================
export type {
    // 图表相关类型
    ChartCategory,
    ChartType,
    ChartConfig,
    ChartFieldMapping,
    ChartStyleConfig,
    ChartInstance,
    // 数据源相关类型
    DataSourceType,
    FileType,
    FieldDataType,
    DataField,
    DataSource,
    ParsedData,
    // 存储相关类型
    StoredChart
} from '@/types/visualization';

// 导出存储管理器
export { ChartStorageManager, STORAGE_KEYS } from '@/types/visualization';
