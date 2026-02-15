# AI PPT Platform - 项目规则

本文档定义了项目必须遵守的核心规则，所有 Agent 在工作过程中必须严格遵循。

---

## 一、代码规范

**详细代码规范请查阅**：[docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md)

该文档包含：
- 前端代码规范（JavaScript / TypeScript）- 腾讯 AlloyTeam 规范
- 后端代码规范（Python）- PEP 8 规范
- CSS 规范
- 通用规范
- 检查命令

**强制要求**：所有 Agent 在生成代码前，必须先阅读并理解 `docs/CODING_STANDARDS.md` 中的规范内容。

---

## 二、API 文档规范

### 1. API 契约文档

- **文档位置**：`docs/architecture/API_CONTRACT.md`
- **强制要求**：所有 Agent 编写新 API 时，必须同步更新此文档

### 2. 文档更新规则

- **BackendEngineer**：新增 API 端点后，必须按照 API_CONTRACT.md 现有格式记录接口信息
- **FrontendEngineer**：调用 API 前必须查阅 API_CONTRACT.md，确保接口定义一致
- **接口变更**：任何 API 的修改（参数、响应、路径等）都必须同步更新文档

### 3. 前后端协作流程

1. **后端开发**：实现 API → 更新 API_CONTRACT.md → 通知前端
2. **前端开发**：查阅 API_CONTRACT.md → 实现接口调用 → 遇到问题反馈后端
3. **接口变更**：后端修改 API → 更新文档 → 前端同步修改

---

## 三、项目结构

```
ai-ppt-platform/
├── backend/                # Python FastAPI 后端
│   └── src/ai_ppt/        # 源代码
├── frontend/              # Next.js 前端
│   ├── app/              # 页面路由
│   ├── components/       # 组件
│   └── lib/              # 工具库
├── docs/                  # 文档
│   ├── CODING_STANDARDS.md    # 代码规范详细文档
│   └── architecture/          # 架构文档
│       └── API_CONTRACT.md    # API 契约文档
└── docker/               # Docker 配置
```

---

## 四、服务端口

| 服务 | 端口 |
|------|------|
| 前端 | 3001 |
| 后端 | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

---

**重要提醒**：所有 Agent 在开始工作前，必须先查阅相关规范文档，确保代码风格一致、接口定义清晰。
