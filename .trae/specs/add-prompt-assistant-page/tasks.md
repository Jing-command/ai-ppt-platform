# Tasks

- [x] Task 1: 创建后端聊天 API 端点
  - [x] SubTask 1.1: 创建聊天相关的 Schema（ChatRequest, ChatResponse, ChatMessage）
  - [x] SubTask 1.2: 创建聊天端点 `/api/v1/chat`，支持流式响应
  - [x] SubTask 1.3: 实现 AI 服务调用逻辑（模拟或集成 LLM）
  - [x] SubTask 1.4: 注册路由到 main.py

- [x] Task 2: 创建前端聊天组件
  - [x] SubTask 2.1: 创建 ChatMessage 组件（消息气泡）
  - [x] SubTask 2.2: 创建 ChatInput 组件（输入框 + 发送按钮）
  - [x] SubTask 2.3: 创建 PromptCard 组件（优化后的提示词卡片）
  - [x] SubTask 2.4: 创建 QuickEntry 组件（快捷入口卡片）

- [x] Task 3: 创建提示词助手页面
  - [x] SubTask 3.1: 创建 `/tips/prompts` 页面布局
  - [x] SubTask 3.2: 实现聊天状态管理
  - [x] SubTask 3.3: 实现流式响应处理
  - [x] SubTask 3.4: 实现"使用此提示词"跳转功能

- [x] Task 4: 更新 Dashboard 页面链接
  - [x] SubTask 4.1: 将"提示词技巧"入口链接指向 `/tips/prompts`

- [x] Task 5: 更新 API 契约文档
  - [x] SubTask 5.1: 在 API_CONTRACT.md 中添加聊天 API 文档

# Task Dependencies
- Task 2 依赖 Task 1（需要 API 端点）
- Task 3 依赖 Task 2（需要组件）
- Task 4, Task 5 可与 Task 3 并行
