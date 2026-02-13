# 项目决策记录

**项目**: AI PPT Platform  
**最后更新**: 2026-02-13

---

## 架构决策

### 1. 技术栈选择
- **后端**: FastAPI + SQLAlchemy 2.0 + SQLite
- **前端**: Next.js 14 + TypeScript + Tailwind
- **AI**: DeepSeek API (异步任务)
- **导出**: python-pptx + reportlab + PIL

### 2. 数据库设计
- SQLite 开发环境
- PostgreSQL 生产环境（预留）
- JSON 字段存储 pages/slides

### 3. API设计
- RESTful API
- JWT 认证
- 异步任务 (Celery)

---

## 关键决策

### 2026-02-12
- ✅ 使用页数模式（用户选15页→生成15页大纲）
- ✅ 每页包含插图提示词
- ✅ 背景设置支持AI/上传/纯色三种方式

### 2026-02-13
- ✅ 安装 MCP 服务: GitHub/Puppeteer/ESLint
- ✅ 全局配置，所有项目可用
- ✅ 自动触发规则定义

---

## 变更历史

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-02-13 | user_id → owner_id | 与数据库字段统一 |
| 2026-02-13 | 添加 MCP 配置 | 增强工具能力 |

---

*文件路径*: `/root/.openclaw/workspace/ai-ppt-platform/.context-compression/decisions.md`
