# Tasks

## Phase 1: 基础架构

- [x] Task 1: 安装依赖和创建类型定义
  - [x] SubTask 1.1: 安装 ECharts、echarts-for-react、xlsx、papaparse 依赖
  - [x] SubTask 1.2: 创建 `frontend/types/visualization.ts` 类型定义文件
  - [x] SubTask 1.3: 创建 `frontend/lib/charts/chartConfigs.ts` 图表配置数据
  - [x] SubTask 1.4: 创建 `frontend/lib/charts/dataParser.ts` 数据解析工具

- [x] Task 2: 创建后端 API
  - [x] SubTask 2.1: 创建 `backend/src/ai_ppt/api/v1/schemas/chart.py` Schema 定义
  - [x] SubTask 2.2: 创建 `backend/src/ai_ppt/services/chart_service.py` 服务逻辑
  - [x] SubTask 2.3: 创建 `backend/src/ai_ppt/api/v1/endpoints/chart.py` API 端点
  - [x] SubTask 2.4: 注册路由到 router.py
  - [x] SubTask 2.5: 更新 API_CONTRACT.md

## Phase 2: 前端组件

- [x] Task 3: 创建图表选择组件
  - [x] SubTask 3.1: 创建 `frontend/components/visualization/ChartSelector/index.tsx` 主组件
  - [x] SubTask 3.2: 创建 `frontend/components/visualization/ChartSelector/ChartCard.tsx` 图表卡片
  - [x] SubTask 3.3: 创建 `frontend/components/visualization/ChartSelector/CategoryTabs.tsx` 分类标签
  - [x] SubTask 3.4: 创建 `frontend/components/visualization/index.ts` 导出索引

- [x] Task 4: 创建数据源组件
  - [x] SubTask 4.1: 创建 `frontend/components/visualization/DataSourceSelector/index.tsx` 主组件
  - [x] SubTask 4.2: 创建 `frontend/components/visualization/DataSourceSelector/FileUploader.tsx` 文件上传

- [x] Task 5: 创建图表预览组件
  - [x] SubTask 5.1: 创建 `frontend/components/visualization/ChartPreview/index.tsx` 主组件
  - [x] SubTask 5.2: 创建 `frontend/components/visualization/ChartPreview/EChartsRenderer.tsx` ECharts 渲染
  - [x] SubTask 5.3: 创建 `frontend/components/visualization/ChartPreview/FieldMapper.tsx` 字段映射
  - [x] SubTask 5.4: 创建 `frontend/components/visualization/ChartPreview/StyleEditor.tsx` 样式编辑

- [x] Task 6: 创建 AI 推荐组件
  - [x] SubTask 6.1: 创建 `frontend/components/visualization/AIRecommend/index.tsx` 主组件
  - [x] SubTask 6.2: 创建 `frontend/components/visualization/AIRecommend/RecommendCard.tsx` 推荐卡片

- [x] Task 7: 创建暂存图表组件
  - [x] SubTask 7.1: 创建 `frontend/components/visualization/StoredCharts/index.tsx` 主组件
  - [x] SubTask 7.2: 创建 `frontend/components/visualization/StoredCharts/StoredChartCard.tsx` 暂存卡片

## Phase 3: 页面实现

- [x] Task 8: 创建图表选择主页
  - [x] SubTask 8.1: 创建 `frontend/app/tips/visualization/page.tsx` 主页
  - [x] SubTask 8.2: 实现图表分类展示
  - [x] SubTask 8.3: 实现 AI 辅助入口

- [x] Task 9: 创建图表创建页
  - [x] SubTask 9.1: 创建 `frontend/app/tips/visualization/create/page.tsx` 创建页
  - [x] SubTask 9.2: 实现数据源选择流程
  - [x] SubTask 9.3: 实现字段映射和图表预览
  - [x] SubTask 9.4: 实现暂存功能

- [x] Task 10: 创建 AI 辅助页
  - [x] SubTask 10.1: 创建 `frontend/app/tips/visualization/ai-assist/page.tsx` AI 辅助页
  - [x] SubTask 10.2: 实现数据上传和分析
  - [x] SubTask 10.3: 实现推荐结果展示

## Phase 4: API 集成

- [x] Task 11: 创建前端 API 函数
  - [x] SubTask 11.1: 创建 `frontend/lib/api/chart.ts` API 函数
  - [x] SubTask 11.2: 集成到各页面组件

## Phase 5: 测试

- [x] Task 12: 编写测试文件
  - [x] SubTask 12.1: 编写后端 API 测试
  - [x] SubTask 12.2: 编写前端组件测试
  - [x] SubTask 12.3: 运行测试并生成报告

## Phase 6: 收尾

- [x] Task 13: 更新 Dashboard 链接
  - [x] SubTask 13.1: 将"数据可视化"入口链接指向 `/tips/visualization`

# Task Dependencies
- Task 2 依赖 Task 1（需要类型定义）
- Task 3-7 可并行（组件开发）
- Task 8-10 依赖 Task 3-7（需要组件）
- Task 11 依赖 Task 2（需要后端 API）
- Task 12 依赖 Task 1-11（需要完整功能）
- Task 13 可与 Task 12 并行
