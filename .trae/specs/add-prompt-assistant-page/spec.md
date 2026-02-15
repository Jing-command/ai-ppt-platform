# AI 提示词助手页面 Spec

## Why

用户在创建 PPT 时往往不知道如何描述自己的需求，导致生成的 PPT 不够理想。需要一个 AI 辅助页面帮助用户优化提示词、明确主题方向、获取创意灵感。

## What Changes

* 新增 `/tips/prompts` 前端页面，提供 AI 聊天交互界面

* 新增 `/api/v1/chat` 后端端点，支持流式响应

* 左侧快捷入口卡片帮助用户快速开始对话

* 右侧聊天区域支持用户与 AI 实时对话

* AI 可生成优化后的提示词卡片，支持一键跳转到大纲生成页

## Impact

* Affected specs: 新增聊天功能

* Affected code:

  * 前端：`frontend/app/tips/prompts/page.tsx`（新）

  * 前端：`frontend/components/chat/`（新）

  * 后端：`backend/src/ai_ppt/api/v1/endpoints/chat.py`（新）

  * 后端：`backend/src/ai_ppt/api/v1/schemas/chat.py`（新）

## ADDED Requirements

### Requirement: AI 聊天页面

系统应提供一个 AI 提示词助手页面，帮助用户优化 PPT 主题描述。

#### Scenario: 用户进入页面

* **WHEN** 用户访问 `/tips/prompts`

* **THEN** 显示左侧快捷入口和右侧聊天区域

* **AND** AI 自动发送欢迎消息

#### Scenario: 用户选择快捷入口

* **WHEN** 用户点击左侧快捷入口卡片

* **THEN** 自动在聊天框填入对应的引导问题

* **AND** AI 开始回复相关建议

#### Scenario: 用户发送消息

* **WHEN** 用户输入消息并发送

* **THEN** 消息显示在聊天区域

* **AND** AI 以流式方式回复

#### Scenario: AI 生成优化提示词

* **WHEN** AI 认为已收集足够信息

* **THEN** 显示优化后的提示词卡片

* **AND** 卡片包含"复制"和"使用此提示词"按钮

#### Scenario: 使用优化后的提示词

* **WHEN** 用户点击"使用此提示词"

* **THEN** 跳转到 `/outlines/new` 页面

* **AND** 自动填入优化后的提示词

### Requirement: 聊天 API 端点

系统应提供聊天 API 端点，支持流式响应。

#### Scenario: 发送聊天请求

* **WHEN** 前端发送 POST `/api/v1/chat`

* **THEN** 返回 SSE 流式响应

* **AND** 每个 chunk 包含部分 AI 回复内容

### Requirement: 快捷入口功能

系统应提供以下快捷入口：

* 优化提示词：帮助用户改进已有的 PPT 描述

* 明确主题：通过问答引导用户明确方向

* 创意灵感：提供相关案例和创意建议

* 受众分析：分析目标观众，推荐内容策略

