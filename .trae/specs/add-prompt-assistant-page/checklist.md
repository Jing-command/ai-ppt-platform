# Checklist

## 后端实现
- [x] ChatRequest Schema 定义正确，包含 messages 字段
- [x] ChatResponse Schema 定义正确，支持流式响应
- [x] POST /api/v1/chat 端点返回 SSE 流式响应
- [x] AI 服务调用逻辑正确处理用户消息

## 前端组件
- [x] ChatMessage 组件正确区分用户和 AI 消息样式
- [x] ChatInput 组件支持回车发送和按钮发送
- [x] PromptCard 组件显示优化后的提示词
- [x] QuickEntry 组件显示快捷入口选项

## 页面功能
- [x] 页面加载时 AI 自动发送欢迎消息
- [x] 点击快捷入口自动填入引导问题
- [x] 流式响应正确显示打字机效果
- [x] "使用此提示词"按钮正确跳转并填入内容
- [x] "复制"按钮正确复制提示词到剪贴板

## 集成测试
- [x] Dashboard 页面"提示词技巧"链接指向 /tips/prompts
- [x] API_CONTRACT.md 已更新聊天 API 文档
