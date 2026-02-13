# AI PPT Platform

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <b>AI 驱动的智能演示文稿生成平台</b><br/>
  让 AI 帮你创建专业 PPT，支持数据连接、智能大纲生成和多格式导出
</p>

<p align="center">
  <a href="#-功能特性">功能特性</a> •
  <a href="#-技术栈">技术栈</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-api-文档">API 文档</a> •
  <a href="#-项目结构">项目结构</a>
</p>

---

## ✨ 功能特性

### 🤖 AI 智能生成
- **主题生成** - 输入主题，AI 自动生成完整大纲
- **智能建议** - 根据内容推荐页面布局和配图提示
- **多语言支持** - 支持中英文内容生成

### 📝 大纲编辑器
- **可视化编辑** - 拖拽式大纲结构调整
- **章节管理** - 轻松添加、删除、重排章节
- **实时预览** - 大纲变动实时同步到 PPT

### 🎨 PPT 编辑器
- **幻灯片编辑** - 支持文本、图片、图表编辑
- **主题切换** - 内置 4+ 套商务主题（浅色/深色/蓝色/绿色）
- **撤销重做** - 50 步历史记录，Command 模式实现

### 🔌 数据连接器
- **MySQL** - 直接连接数据库生成数据报告
- **Salesforce** - 集成 CRM 数据到演示文稿
- **更多数据源** - 可扩展的数据连接架构

### 📤 多格式导出
- **PPTX** - 原生 PowerPoint 格式，可二次编辑
- **PDF** - 高清 PDF 文档导出
- **图片** - PNG/JPG 格式，支持单页或批量导出
- **异步处理** - 大文件导出不卡顿

### 🔐 企业级安全
- **JWT 认证** - Access Token + Refresh Token 机制
- **密码加密** - bcrypt 哈希存储
- **API 限流** - 防止恶意请求

---

## 🛠 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | ^0.115 | 高性能 Web 框架 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ^2.0 | 异步 ORM |
| [Pydantic](https://docs.pydantic.dev/) | ^2.10 | 数据验证 |
| [python-pptx](https://python-pptx.readthedocs.io/) | ^1.0 | PPTX 文件生成 |
| [ReportLab](https://www.reportlab.com/) | ^3.6 | PDF 生成 |
| [Pillow](https://pillow.readthedocs.io/) | ^12.1 | 图片处理 |
| [Alembic](https://alembic.sqlalchemy.org/) | ^1.14 | 数据库迁移 |
| [Pytest](https://docs.pytest.org/) | ^8.3 | 测试框架 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| [Next.js](https://nextjs.org/) | 14.2 | React 全栈框架 |
| [TypeScript](https://www.typescriptlang.org/) | ^5.4 | 类型安全 |
| [Tailwind CSS](https://tailwindcss.com/) | ^3.4 | 原子化 CSS |
| [Dnd Kit](https://dndkit.com/) | ^6.3 | 拖拽排序 |
| [Framer Motion](https://www.framer.com/motion/) | ^12.34 | 动画效果 |
| [React Hook Form](https://react-hook-form.com/) | ^7.51 | 表单管理 |
| [Zod](https://zod.dev/) | ^3.22 | 数据验证 |

---

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-ppt-platform.git
cd ai-ppt-platform
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动服务
PYTHONPATH=./src uvicorn ai_ppt.main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将运行在: http://localhost:8000

### 3. 前端启动

```bash
cd my-app

# 安装依赖
npm install

# 开发模式
npm run dev
```

前端应用将运行在: http://localhost:3000

### 4. 访问应用

打开浏览器访问 http://localhost:3000

测试账户:
- 邮箱: `demo@example.com`
- 密码: `123456`

---

## 📚 API 文档

启动后端后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 核心 API 端点

```
POST   /api/v1/auth/register          # 用户注册
POST   /api/v1/auth/login             # 用户登录
POST   /api/v1/auth/refresh           # 刷新 Token

GET    /api/v1/outlines               # 获取大纲列表
POST   /api/v1/outlines               # 创建大纲
POST   /api/v1/outlines/generate      # AI 生成大纲
GET    /api/v1/outlines/{id}          # 获取大纲详情
PUT    /api/v1/outlines/{id}          # 更新大纲
DELETE /api/v1/outlines/{id}          # 删除大纲

GET    /api/v1/presentations          # 获取 PPT 列表
POST   /api/v1/presentations          # 创建 PPT
GET    /api/v1/presentations/{id}     # 获取 PPT 详情
PUT    /api/v1/presentations/{id}     # 更新 PPT
DELETE /api/v1/presentations/{id}     # 删除 PPT

POST   /api/v1/exports/pptx           # 导出 PPTX
POST   /api/v1/exports/pdf            # 导出 PDF
POST   /api/v1/exports/images         # 导出图片
GET    /api/v1/exports/{id}/status    # 查询导出状态
GET    /api/v1/exports/{id}/download  # 下载文件

GET    /api/v1/connectors            # 获取连接器列表
POST   /api/v1/connectors            # 创建连接器
POST   /api/v1/connectors/{id}/test  # 测试连接
```

---

## 📁 项目结构

```
ai-ppt-platform/
├── backend/                      # 后端代码
│   ├── src/ai_ppt/
│   │   ├── api/v1/endpoints/    # API 端点
│   │   │   ├── auth.py          # 认证相关
│   │   │   ├── outlines.py      # 大纲管理
│   │   │   ├── presentations.py # PPT 管理
│   │   │   ├── exports.py       # 导出功能
│   │   │   └── connectors.py    # 数据连接
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── export_service.py    # 导出服务
│   │   │   ├── outline_service.py   # 大纲服务
│   │   │   └── outline_generation.py # AI 生成
│   │   ├── models/              # 数据模型
│   │   ├── domain/              # 领域模型
│   │   ├── infrastructure/      # 基础设施
│   │   └── main.py              # 应用入口
│   ├── tests/                   # 测试文件
│   ├── alembic/                 # 数据库迁移
│   ├── pyproject.toml           # Poetry 配置
│   └── requirements.txt         # pip 依赖
│
├── my-app/                       # 前端代码
│   ├── app/                     # Next.js 页面
│   │   ├── auth/                # 认证页面
│   │   ├── outlines/            # 大纲页面
│   │   ├── presentations/       # PPT 页面
│   │   └── page.tsx             # 首页
│   ├── components/              # 组件
│   │   ├── auth/                # 认证组件
│   │   ├── outlines/            # 大纲组件
│   │   └── presentations/       # PPT 组件
│   │       ├── ExportButton.tsx     # 导出按钮
│   │       ├── SlideEditor.tsx      # 幻灯片编辑
│   │       └── SlideToolbar.tsx     # 工具栏
│   ├── lib/api/                 # API 客户端
│   │   ├── auth.ts
│   │   ├── outlines.ts
│   │   ├── presentations.ts
│   │   └── exports.ts
│   ├── types/                   # TypeScript 类型
│   └── package.json
│
├── docs/                         # 文档
├── tests/                        # 集成测试
├── DEPS.md                       # 依赖说明
├── API_CONTRACT.md               # API 契约
└── README.md                     # 本文件
```

---

## 🧪 测试

### 后端测试

```bash
cd backend
pytest tests/ -v --tb=short
```

### 导出功能测试

```bash
python tests/test_export_system.py
```

---

## 📸 界面预览

### 大纲编辑器
- 左侧：章节结构树
- 右侧：编辑区域
- 底部：AI 生成按钮

### PPT 编辑器
- 左侧：幻灯片缩略图
- 中间：编辑画布
- 右侧：属性面板
- 顶部：工具栏 + 导出按钮

### 导出功能
- 支持 PPTX/PDF/PNG/JPG
- 实时进度显示
- 一键下载

---

## 🛣️ 开发路线图

- [x] **Iteration 1**: 用户认证系统
- [x] **Iteration 2**: 连接器管理 (MySQL/Salesforce)
- [x] **Iteration 3**: 大纲编辑器 + AI 生成
- [x] **Iteration 4**: PPT 编辑器
- [x] **Iteration 5**: 导出系统 (PPTX/PDF/图片)
- [ ] **Iteration 6**: 协作编辑 / 模板市场 / AI 优化

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

[MIT](LICENSE) © 2026 AI PPT Platform

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 卓越的后端框架
- [Next.js](https://nextjs.org/) - 强大的前端框架
- [OpenAI](https://openai.com/) / DeepSeek - AI 能力支持

---

<p align="center">
  如果这个项目对你有帮助，请给它一个 ⭐️
</p>
