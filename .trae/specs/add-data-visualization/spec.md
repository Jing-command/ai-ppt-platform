# 数据可视化功能 Spec

## Why
用户需要专业的图表创建工具来增强 PPT 的数据展示能力。当前系统缺乏数据可视化功能，用户无法在 PPT 中插入专业的数据图表。

## What Changes
- 新增 `/tips/visualization` 图表选择主页
- 新增 `/tips/visualization/create` 图表创建页
- 新增 `/tips/visualization/ai-assist` AI 辅助选图页
- 新增后端 `/api/v1/charts/*` 系列端点
- 新增前端可视化组件库
- 支持 Excel、CSV、JSON 文件上传
- 支持数据库连接读取数据
- 支持图表暂存到 localStorage

## Impact
- Affected specs: 新增数据可视化模块
- Affected code:
  - 前端：`frontend/app/tips/visualization/`（新）
  - 前端：`frontend/components/visualization/`（新）
  - 前端：`frontend/lib/charts/`（新）
  - 前端：`frontend/lib/api/chart.ts`（新）
  - 后端：`backend/src/ai_ppt/api/v1/endpoints/chart.py`（新）
  - 后端：`backend/src/ai_ppt/api/v1/schemas/chart.py`（新）
  - 后端：`backend/src/ai_ppt/services/chart_service.py`（新）

## ADDED Requirements

### Requirement: 图表选择主页
系统应提供图表选择主页，展示所有可用图表类型。

#### Scenario: 用户浏览图表
- **WHEN** 用户访问 `/tips/visualization`
- **THEN** 显示按分类组织的图表卡片
- **AND** 每个卡片显示图表名称、图标、描述
- **AND** 提供 AI 辅助选图入口

#### Scenario: 用户选择图表
- **WHEN** 用户点击某个图表卡片
- **THEN** 跳转到图表创建页
- **AND** URL 携带图表类型参数

### Requirement: 图表创建页
系统应提供图表创建页，支持数据配置和图表生成。

#### Scenario: 用户上传文件
- **WHEN** 用户上传 Excel、CSV 或 JSON 文件
- **THEN** 系统解析文件内容
- **AND** 显示数据预览和字段信息

#### Scenario: 用户配置字段映射
- **WHEN** 用户选择维度和度量字段
- **THEN** 实时预览图表效果
- **AND** 支持调整样式配置

#### Scenario: 用户暂存图表
- **WHEN** 用户点击"暂存到PPT"
- **THEN** 图表配置保存到 localStorage
- **AND** 显示暂存成功提示

### Requirement: AI 辅助选图
系统应提供 AI 辅助选图功能，根据数据特征推荐图表。

#### Scenario: AI 分析数据
- **WHEN** 用户上传数据并点击"AI 分析推荐"
- **THEN** AI 分析数据特征
- **AND** 返回 3 个推荐图表（带预览和推荐理由）

#### Scenario: 用户选择推荐图表
- **WHEN** 用户选择一个推荐图表
- **THEN** 进入图表编辑页
- **AND** 预填充推荐的配置

### Requirement: 图表 API 端点
系统应提供图表相关 API 端点。

#### Scenario: 数据分析
- **WHEN** 前端发送 POST `/api/v1/charts/analyze`
- **THEN** 返回字段信息和数据建议

#### Scenario: 图表生成
- **WHEN** 前端发送 POST `/api/v1/charts/generate`
- **THEN** 返回 ECharts 配置

#### Scenario: AI 推荐
- **WHEN** 前端发送 POST `/api/v1/charts/recommend`
- **THEN** 返回推荐图表列表
