# AI PPT Platform 依赖说明

## 📦 后端依赖 (Python)

### 管理工具
- **Poetry** - Python 包管理和虚拟环境管理

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **fastapi** | ^0.115.0 | Web 框架 |
| **uvicorn** | ^0.32.0 | ASGI 服务器 |
| **pydantic** | ^2.10.0 | 数据验证 |
| **pydantic-settings** | ^2.7.0 | 配置管理 |
| **sqlalchemy** | ^2.0.36 | ORM 数据库操作 |
| **asyncpg** | ^0.30.0 | PostgreSQL 异步驱动 |
| **alembic** | ^1.14.0 | 数据库迁移 |
| **httpx** | ^0.28.0 | HTTP 客户端 |
| **python-pptx** | ^1.0.2 | PPTX 文件生成 |
| **reportlab** | ^3.6.12 | PDF 文件生成 |
| **pillow** | (隐含) | 图片处理 |
| **jinja2** | ^3.1.0 | 模板引擎 |
| **python-multipart** | ^0.0.20 | 文件上传支持 |
| **python-jose** | ^3.3.0 | JWT 认证 |
| **passlib** | ^1.7.4 | 密码哈希 |
| **redis** | ^5.2.0 | 缓存和消息队列 |
| **aiomysql** | ^0.2.0 | MySQL 异步驱动 |
| **aiofiles** | ^24.1.0 | 异步文件操作 |
| **structlog** | ^24.4.0 | 结构化日志 |
| **sentry-sdk** | ^2.19.0 | 错误监控 |

### 开发依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **pytest** | ^8.3.0 | 测试框架 |
| **pytest-asyncio** | ^0.25.0 | 异步测试支持 |
| **pytest-cov** | ^6.0.0 | 测试覆盖率 |
| **respx** | ^0.21.0 | HTTP 请求模拟 |
| **factory-boy** | ^3.3.0 | 测试数据工厂 |
| **faker** | ^33.1.0 | 假数据生成 |
| **mypy** | ^1.13.0 | 类型检查 |
| **ruff** | ^0.8.0 | 代码格式化和检查 |
| **pre-commit** | ^4.0.0 | Git 钩子管理 |

### 安装命令

```bash
# 使用 Poetry 安装（推荐）
cd backend
poetry install

# 或使用 pip 安装
pip install -r requirements.txt
```

### 导出 requirements.txt

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

## 🎨 前端依赖 (Node.js)

### 管理工具
- **npm** 或 **yarn** - Node.js 包管理器

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **next** | 14.2.0 | React 框架 |
| **react** | ^18.2.0 | UI 库 |
| **react-dom** | ^18.2.0 | React DOM |
| **axios** | ^1.6.0 | HTTP 客户端 |
| **@dnd-kit/core** | ^6.3.1 | 拖拽功能核心 |
| **@dnd-kit/sortable** | ^10.0.0 | 拖拽排序 |
| **@dnd-kit/utilities** | ^3.2.2 | 拖拽工具 |
| **@hookform/resolvers** | ^3.3.0 | 表单验证 |
| **react-hook-form** | ^7.51.0 | 表单管理 |
| **zod** | ^3.22.0 | 数据验证 |
| **framer-motion** | ^12.34.0 | 动画库 |
| **lucide-react** | ^0.563.0 | 图标库 |

### 开发依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **typescript** | ^5.4.0 | 类型系统 |
| **@types/node** | ^20.11.0 | Node.js 类型 |
| **@types/react** | ^18.2.0 | React 类型 |
| **@types/react-dom** | ^18.2.0 | React DOM 类型 |
| **tailwindcss** | ^3.4.0 | CSS 框架 |
| **postcss** | ^8.4.0 | CSS 处理 |
| **autoprefixer** | ^10.4.0 | CSS 前缀 |
| **eslint** | ^8.57.0 | 代码检查 |
| **eslint-config-next** | 14.2.0 | Next.js ESLint 配置 |

### 安装命令

```bash
cd my-app
npm install

# 或
yarn install
```

---

## 🐳 Docker 依赖

如果需要使用 Docker 部署，需要以下镜像：

| 镜像 | 版本 | 用途 |
|------|------|------|
| **python** | 3.11-slim | 后端运行环境 |
| **node** | 18-alpine | 前端构建环境 |
| **postgres** | 15-alpine | 数据库 |
| **redis** | 7-alpine | 缓存/队列 |

---

## 🔧 系统要求

### 后端
- **Python**: 3.11+
- **PostgreSQL**: 15+ (可选，默认使用 SQLite)
- **Redis**: 7+ (可选，用于 Celery)

### 前端
- **Node.js**: 18+
- **npm**: 9+ 或 **yarn**: 1.22+

---

## 📋 快速启动

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
PYTHONPATH=./src uvicorn ai_ppt.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 前端启动

```bash
cd my-app

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
npm start
```

---

## 📝 依赖文件位置

```
ai-ppt-platform/
├── backend/
│   ├── pyproject.toml      # Poetry 依赖定义
│   └── requirements.txt    # pip 依赖 (可选导出)
└── my-app/
    └── package.json        # npm 依赖
```

---

*最后更新: 2026-02-13*
