# 数据可视化功能开发文档

## 一、功能概述

数据可视化模块为用户提供专业的图表创建和 AI 辅助选图功能，支持多种数据源接入，生成的图表可暂存并在 PPT 制作中使用。

### 核心功能

| 功能 | 描述 |
|------|------|
| 图表选择 | 提供 20+ 种专业图表类型供用户选择 |
| 数据上传 | 支持 Excel、CSV、JSON 文件上传 |
| 数据库连接 | 连接公司内部数据库读取数据 |
| AI 辅助选图 | AI 分析数据特征，推荐最适合的图表类型 |
| 图表预览 | 实时预览生成的图表，支持调整配置 |
| PPT 暂存 | 将图表暂存到 localStorage，供 PPT 制作使用 |

---

## 二、技术选型

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| ECharts | ^5.5.0 | 图表渲染引擎 |
| echarts-for-react | ^3.0.0 | React 封装组件 |
| xlsx | ^0.18.0 | Excel 文件解析 |
| papaparse | ^5.4.0 | CSV 文件解析 |

### 安装命令

```bash
npm install echarts echarts-for-react xlsx papaparse
```

### 地图资源

ECharts 地图数据需要单独引入：

```javascript
// 中国地图
import * as echarts from 'echarts';
import chinaJson from 'echarts/map/json/china.json';
echarts.registerMap('china', chinaJson);

// 世界地图
import worldJson from 'echarts/map/json/world.json';
echarts.registerMap('world', worldJson);
```

---

## 三、页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/tips/visualization` | 图表选择主页 | 展示所有图表类型 + AI 辅助入口 |
| `/tips/visualization/create` | 图表创建页 | 数据配置 + 图表生成 |
| `/tips/visualization/ai-assist` | AI 辅助页 | AI 分析并推荐图表 |

---

## 四、图表类型定义

### 4.1 图表分类

```typescript
// types/visualization.ts

/** 图表分类 */
export type ChartCategory = 'basic' | 'advanced' | 'business' | 'creative' | 'map';

/** 图表类型 */
export type ChartType =
  // 基础图表
  | 'bar'           // 柱状图
  | 'line'          // 折线图
  | 'pie'           // 饼图
  | 'scatter'       // 散点图
  | 'area'          // 面积图
  | 'radar'         // 雷达图
  // 高级图表
  | 'bubble'        // 气泡图
  | 'heatmap'       // 热力图
  | 'treemap'       // 矩形树图
  | 'sunburst'      // 旭日图
  | 'sankey'        // 桑基图
  // 商业图表
  | 'gauge'         // 仪表盘
  | 'funnel'        // 漏斗图
  | 'waterfall'     // 瀑布图
  | 'boxplot'       // 箱线图
  // 地图
  | 'map-china'     // 中国地图
  | 'map-world'     // 世界地图
  | 'map-scatter'   // 地图散点
  | 'map-heatmap';  // 地图热力

/** 图表配置 */
export interface ChartConfig {
  id: string;
  type: ChartType;
  category: ChartCategory;
  name: string;
  nameEn: string;
  icon: string;
  description: string;
  useCases: string[];           // 适用场景
  dataRequirements: {           // 数据要求
    minDimensions: number;      // 最小维度数
    minMeasures: number;        // 最小度量数
    supportsMultiSeries: boolean;
  };
  defaultOption: Record<string, unknown>;  // ECharts 默认配置
}
```

### 4.2 图表配置数据

```typescript
// lib/charts/chartConfigs.ts

export const chartConfigs: ChartConfig[] = [
  // 基础图表
  {
    id: 'bar',
    type: 'bar',
    category: 'basic',
    name: '柱状图',
    nameEn: 'Bar Chart',
    icon: 'bar-chart-2',
    description: '用于比较不同类别的数值大小',
    useCases: ['销售对比', '业绩排名', '季度分析'],
    dataRequirements: {
      minDimensions: 1,
      minMeasures: 1,
      supportsMultiSeries: true
    },
    defaultOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category' },
      yAxis: { type: 'value' },
      series: [{ type: 'bar' }]
    }
  },
  {
    id: 'line',
    type: 'line',
    category: 'basic',
    name: '折线图',
    nameEn: 'Line Chart',
    icon: 'trending-up',
    description: '用于展示数据随时间变化的趋势',
    useCases: ['趋势分析', '股价走势', '用户增长'],
    dataRequirements: {
      minDimensions: 1,
      minMeasures: 1,
      supportsMultiSeries: true
    },
    defaultOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category' },
      yAxis: { type: 'value' },
      series: [{ type: 'line', smooth: true }]
    }
  },
  {
    id: 'pie',
    type: 'pie',
    category: 'basic',
    name: '饼图',
    nameEn: 'Pie Chart',
    icon: 'pie-chart',
    description: '用于展示各部分占整体的比例',
    useCases: ['市场份额', '预算分配', '人口构成'],
    dataRequirements: {
      minDimensions: 1,
      minMeasures: 1,
      supportsMultiSeries: false
    },
    defaultOption: {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    }
  },
  // 地图图表
  {
    id: 'map-china',
    type: 'map-china',
    category: 'map',
    name: '中国地图',
    nameEn: 'China Map',
    icon: 'map',
    description: '在中国地图上展示各省份的数据分布',
    useCases: ['销售分布', '用户地域分析', '物流覆盖'],
    dataRequirements: {
      minDimensions: 1,
      minMeasures: 1,
      supportsMultiSeries: false
    },
    defaultOption: {
      tooltip: { trigger: 'item' },
      visualMap: {
        min: 0,
        max: 100,
        text: ['高', '低'],
        inRange: {
          color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
        }
      },
      series: [{
        type: 'map',
        map: 'china',
        roam: true,
        label: { show: true },
        emphasis: { label: { show: true } }
      }]
    }
  }
  // ... 更多图表配置
];
```

---

## 五、数据结构定义

### 5.1 数据源类型

```typescript
// types/visualization.ts

/** 数据源类型 */
export type DataSourceType = 'file' | 'database';

/** 文件类型 */
export type FileType = 'excel' | 'csv' | 'json';

/** 数据源配置 */
export interface DataSource {
  id: string;
  type: DataSourceType;
  name: string;
  // 文件类型
  fileType?: FileType;
  fileName?: string;
  fileData?: unknown[];
  // 数据库类型
  connectorId?: string;
  tableName?: string;
  query?: string;
  // 通用
  createdAt: string;
  updatedAt: string;
}

/** 数据字段 */
export interface DataField {
  name: string;           // 字段名
  type: 'dimension' | 'measure';  // 维度 or 度量
  dataType: 'string' | 'number' | 'date';  // 数据类型
  sampleValues: unknown[];  // 示例值
}

/** 解析后的数据 */
export interface ParsedData {
  fields: DataField[];    // 字段列表
  rows: Record<string, unknown>[];  // 数据行
  rowCount: number;       // 行数
  columnCount: number;    // 列数
}
```

### 5.2 图表实例

```typescript
// types/visualization.ts

/** 图表字段映射 */
export interface ChartFieldMapping {
  dimension: string[];    // 维度字段
  measure: string[];      // 度量字段
  series?: string;        // 系列字段（可选）
}

/** 图表样式配置 */
export interface ChartStyleConfig {
  title: string;          // 图表标题
  titleVisible: boolean;  // 是否显示标题
  legendVisible: boolean; // 是否显示图例
  colorTheme: string;     // 配色主题
  animation: boolean;     // 是否开启动画
}

/** 图表实例 */
export interface ChartInstance {
  id: string;
  type: ChartType;
  dataSource: DataSource;
  fieldMapping: ChartFieldMapping;
  styleConfig: ChartStyleConfig;
  echartsOption: Record<string, unknown>;  // ECharts 配置
  thumbnail?: string;     // 缩略图 base64
  createdAt: string;
  updatedAt: string;
}
```

### 5.3 暂存数据结构

```typescript
// types/visualization.ts

/** 暂存的图表项 */
export interface StoredChart {
  id: string;
  instance: ChartInstance;
  storedAt: string;
}

/** localStorage 键名 */
export const STORAGE_KEYS = {
  STORED_CHARTS: 'ai-ppt-stored-charts',
  CHART_DRAFT: 'ai-ppt-chart-draft'
} as const;

/** 暂存管理器 */
export class ChartStorageManager {
  private static STORAGE_KEY = STORAGE_KEYS.STORED_CHARTS;

  /** 获取所有暂存图表 */
  static getStoredCharts(): StoredChart[] {
    const data = localStorage.getItem(this.STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  }

  /** 添加暂存图表 */
  static addChart(instance: ChartInstance): StoredChart {
    const charts = this.getStoredCharts();
    const stored: StoredChart = {
      id: `stored_${Date.now()}`,
      instance,
      storedAt: new Date().toISOString()
    };
    charts.push(stored);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(charts));
    return stored;
  }

  /** 删除暂存图表 */
  static removeChart(id: string): void {
    const charts = this.getStoredCharts();
    const filtered = charts.filter(c => c.id !== id);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
  }

  /** 清空所有暂存 */
  static clearAll(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}
```

---

## 六、API 设计

### 6.1 后端 API 端点

#### 图表相关

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/charts/analyze` | 分析数据，返回字段信息 |
| POST | `/api/v1/charts/generate` | 生成图表 ECharts 配置 |
| POST | `/api/v1/charts/recommend` | AI 推荐图表类型 |

#### 请求/响应 Schema

```python
# backend/src/ai_ppt/api/v1/schemas/chart.py

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum

class ChartTypeEnum(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    # ... 其他类型

class DataAnalyzeRequest(BaseModel):
    """数据分析请求"""
    data: List[Dict[str, Any]]  # 数据行
    sample_size: Optional[int] = 1000  # 采样大小

class DataFieldInfo(BaseModel):
    """数据字段信息"""
    name: str
    type: str  # dimension, measure
    data_type: str  # string, number, date
    sample_values: List[Any]
    unique_count: Optional[int] = None
    null_count: Optional[int] = None

class DataAnalyzeResponse(BaseModel):
    """数据分析响应"""
    fields: List[DataFieldInfo]
    row_count: int
    column_count: int
    suggestions: Optional[List[str]] = None  # 数据建议

class ChartGenerateRequest(BaseModel):
    """图表生成请求"""
    chart_type: ChartTypeEnum
    data: List[Dict[str, Any]]
    field_mapping: Dict[str, List[str]]  # dimension, measure, series
    style_config: Optional[Dict[str, Any]] = None

class ChartGenerateResponse(BaseModel):
    """图表生成响应"""
    echarts_option: Dict[str, Any]  # ECharts 配置
    thumbnail: Optional[str] = None  # 缩略图 base64

class ChartRecommendRequest(BaseModel):
    """图表推荐请求"""
    data: List[Dict[str, Any]]
    context: Optional[str] = None  # 用户描述的使用场景

class RecommendedChart(BaseModel):
    """推荐的图表"""
    chart_type: ChartTypeEnum
    chart_name: str
    confidence: float  # 推荐置信度 0-1
    reason: str  # 推荐理由
    echarts_option: Dict[str, Any]  # 预览配置

class ChartRecommendResponse(BaseModel):
    """图表推荐响应"""
    recommendations: List[RecommendedChart]  # 最多3个推荐
```

### 6.2 前端 API 函数

```typescript
// lib/api/chart.ts

import { apiClient } from './client';
import type {
  DataAnalyzeRequest,
  DataAnalyzeResponse,
  ChartGenerateRequest,
  ChartGenerateResponse,
  ChartRecommendRequest,
  ChartRecommendResponse
} from '@/types/visualization';

/** 分析数据 */
export async function analyzeData(data: DataAnalyzeRequest): Promise<DataAnalyzeResponse> {
  const response = await apiClient.post('/api/v1/charts/analyze', data);
  return response.data;
}

/** 生成图表 */
export async function generateChart(data: ChartGenerateRequest): Promise<ChartGenerateResponse> {
  const response = await apiClient.post('/api/v1/charts/generate', data);
  return response.data;
}

/** AI 推荐图表 */
export async function recommendCharts(data: ChartRecommendRequest): Promise<ChartRecommendResponse> {
  const response = await apiClient.post('/api/v1/charts/recommend', data);
  return response.data;
}
```

---

## 七、组件设计

### 7.1 组件结构

```
components/visualization/
├── ChartSelector/          # 图表选择器
│   ├── index.tsx           # 主组件
│   ├── ChartCard.tsx       # 图表卡片
│   └── CategoryTabs.tsx    # 分类标签
├── DataSourceSelector/     # 数据源选择
│   ├── index.tsx           # 主组件
│   ├── FileUploader.tsx    # 文件上传
│   └── DatabaseConnector.tsx # 数据库连接
├── DataPreview/            # 数据预览
│   ├── index.tsx           # 主组件
│   ├── DataTable.tsx       # 数据表格
│   └── FieldMapper.tsx     # 字段映射
├── ChartPreview/           # 图表预览
│   ├── index.tsx           # 主组件
│   ├── EChartsRenderer.tsx # ECharts 渲染
│   └── StyleEditor.tsx     # 样式编辑
├── AIRecommend/            # AI 推荐
│   ├── index.tsx           # 主组件
│   └── RecommendCard.tsx   # 推荐卡片
└── StoredCharts/           # 暂存图表
    ├── index.tsx           # 主组件
    └── StoredChartCard.tsx # 暂存卡片
```

### 7.2 核心组件接口

```typescript
// components/visualization/ChartSelector/index.tsx

interface ChartSelectorProps {
  onSelect: (chartType: ChartType) => void;
  selectedType?: ChartType;
}

// components/visualization/DataSourceSelector/index.tsx

interface DataSourceSelectorProps {
  onSelect: (dataSource: DataSource) => void;
  onFileUpload: (file: File) => Promise<ParsedData>;
  connectors?: Connector[];  // 已连接的数据源
}

// components/visualization/ChartPreview/index.tsx

interface ChartPreviewProps {
  chartType: ChartType;
  data: ParsedData;
  fieldMapping: ChartFieldMapping;
  styleConfig?: ChartStyleConfig;
  onConfigChange: (option: Record<string, unknown>) => void;
  onStore: () => void;
}

// components/visualization/AIRecommend/index.tsx

interface AIRecommendProps {
  data: ParsedData;
  onSelect: (chart: RecommendedChart) => void;
}
```

---

## 八、用户流程

### 8.1 手动选择图表流程

```
用户进入 /tips/visualization
    ↓
浏览图表分类，选择图表类型
    ↓
进入 /tips/visualization/create?type=bar
    ↓
选择数据源（上传文件 或 选择数据库）
    ↓
系统解析数据，展示字段信息
    ↓
用户配置字段映射（维度、度量）
    ↓
实时预览图表效果
    ↓
调整样式配置（标题、配色、动画）
    ↓
点击"暂存到PPT"
    ↓
图表保存到 localStorage
```

### 8.2 AI 辅助选图流程

```
用户点击"AI 辅助选图"
    ↓
进入 /tips/visualization/ai-assist
    ↓
选择数据源（上传文件 或 选择数据库）
    ↓
系统解析数据，展示字段信息
    ↓
点击"AI 分析推荐"
    ↓
AI 分析数据特征
    ↓
展示 3 个推荐图表（带预览）
    ↓
用户选择一个图表
    ↓
进入图表编辑页，可调整配置
    ↓
点击"暂存到PPT"
    ↓
图表保存到 localStorage
```

---

## 九、实现步骤

### Phase 1: 基础架构（2天）

- [ ] 安装 ECharts 相关依赖
- [ ] 创建类型定义文件
- [ ] 创建图表配置数据
- [ ] 实现 localStorage 暂存管理器

### Phase 2: 图表选择主页（1天）

- [ ] 创建 `/tips/visualization` 页面
- [ ] 实现图表分类展示
- [ ] 实现图表卡片组件
- [ ] 实现 AI 辅助入口

### Phase 3: 数据源管理（2天）

- [ ] 实现文件上传组件（支持 Excel、CSV、JSON）
- [ ] 实现数据解析功能
- [ ] 实现数据库连接弹窗
- [ ] 实现数据预览组件

### Phase 4: 图表创建页（2天）

- [ ] 创建 `/tips/visualization/create` 页面
- [ ] 实现字段映射组件
- [ ] 实现 ECharts 渲染组件
- [ ] 实现样式编辑组件
- [ ] 实现暂存功能

### Phase 5: AI 辅助页（2天）

- [ ] 创建 `/tips/visualization/ai-assist` 页面
- [ ] 实现后端 AI 推荐接口
- [ ] 实现推荐结果展示
- [ ] 实现推荐图表选择

### Phase 6: 后端 API（2天）

- [ ] 创建图表相关 Schema
- [ ] 实现数据分析端点
- [ ] 实现图表生成端点
- [ ] 实现 AI 推荐端点
- [ ] 更新 API 契约文档

---

## 十、注意事项

### 10.1 性能优化

- 大数据集需采样后分析（建议最大 10000 行）
- 图表渲染使用防抖处理
- 缩略图生成使用 canvas toDataURL

### 10.2 安全考虑

- 文件上传需限制大小（建议最大 10MB）
- 数据库查询需使用参数化查询防止注入
- 敏感数据不应存储在 localStorage

### 10.3 兼容性

- ECharts 需要支持主流浏览器
- 地图功能需要加载地图 JSON 数据
- 动画效果需考虑低端设备降级

---

## 十一、参考资源

- [ECharts 官方文档](https://echarts.apache.org/zh/index.html)
- [echarts-for-react](https://github.com/hustcc/echarts-for-react)
- [ECharts 地图数据](https://github.com/apache/echarts/tree/master/map)
- [SheetJS (xlsx)](https://docs.sheetjs.com/)
