# AGENTS.md - AI PPT Platform 会话启动指南

**项目**: AI PPT Platform  
**技术栈**: FastAPI + SQLAlchemy + PostgreSQL + React  
**当前迭代**: 迭代 3 完成，迭代 4 待开始

---

## 🚀 快速开始

### 新会话自动加载

每次新会话开始时，**自动执行**:

```bash
./scripts/hooks/on_session_start.sh
```

这会加载:
- ✅ PROJECT_STATE.md - 项目状态和进度
- ✅ task-queue.md - 当前任务队列  
- ✅ API_CONTRACT.md - API 契约
- ✅ memory/ - 历史会话记忆

---

## 📊 项目状态

### 当前进度
- [x] 迭代 1: 用户认证系统 (100%)
- [x] 迭代 2: 连接器管理 (100%)
- [x] 迭代 3: CI/CD 修复 (100%)
- [ ] 迭代 4: 大纲编辑器 (待开始)

### 代码质量
- **测试覆盖**: 83% (780 测试通过)
- **CI/CD**: ✅ 全部通过
- **类型检查**: mypy 0 错误

---

## 📋 任务队列

查看当前任务:
```bash
cat task-queue.md
```

标记任务完成:
```bash
./scripts/hooks/on_task_complete.sh "任务名" "success"
```

---

## 🔌 关键 API

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token

### PPT
- `POST /api/v1/presentations` - 创建 PPT
- `GET /api/v1/presentations/{id}` - 获取 PPT
- `PUT /api/v1/presentations/{id}` - 更新 PPT
- `DELETE /api/v1/presentations/{id}` - 删除 PPT

### 连接器
- `GET /api/v1/connectors` - 列出连接器
- `POST /api/v1/connectors/{id}/query` - 查询数据

详细 API 文档: `API_CONTRACT.md`

---

## 🏗️ 项目结构

```
ai-ppt-platform/
├── backend/
│   ├── src/ai_ppt/
│   │   ├── api/v1/          # API 端点
│   │   ├── application/     # 应用服务层
│   │   ├── domain/          # 领域层
│   │   ├── infrastructure/  # 基础设施层
│   │   └── services/        # 业务服务
│   └── tests/               # 测试 (780 个)
├── frontend/                # React 前端
├── docs/                    # 文档
├── memory/                  # 会话记忆
├── scripts/hooks/           # 自动化钩子
│   ├── on_session_start.sh
│   ├── on_task_complete.sh
│   └── on_ci_complete.sh
├── PROJECT_STATE.md         # 项目状态
├── task-queue.md           # 任务队列
└── API_CONTRACT.md         # API 契约
```

---

## 🎯 下一步任务 (迭代 4)

### 1. AI 生成大纲功能
- [ ] 集成 DeepSeek API
- [ ] 实现大纲生成服务
- [ ] 添加大纲编辑和确认流程

### 2. 大纲可视化编辑器
- [ ] 实现大纲树形结构展示
- [ ] 支持拖拽排序
- [ ] 支持章节增删改

### 3. 连接器数据集成
- [ ] 在大纲中引用数据源
- [ ] 数据预览和验证

---

## 🛠️ 开发规范

### 代码标准
- ✅ 所有 Python 代码必须通过 mypy 类型检查
- ✅ 所有测试必须通过 CI/CD
- ✅ 测试覆盖率必须 >= 80%
- ✅ 遵循 PEP8 代码风格
- ✅ 使用 SQLAlchemy 2.0 语法
- ✅ 使用 Pydantic v2 进行数据验证

### 命名规范
- Python: `snake_case`
- 类名: `PascalCase`
- 常量: `UPPER_SNAKE_CASE`
- 测试文件: `test_*.py`

---

## 🪝 钩子系统

### 可用钩子

**on_session_start** - 新会话启动
```bash
./scripts/hooks/on_session_start.sh
```

**on_task_complete** - 任务完成
```bash
./scripts/hooks/on_task_complete.sh "任务名" "success|failed"
```

**on_ci_complete** - CI/CD 完成
```bash
./scripts/hooks/on_ci_complete.sh "success|failure" "job-name"
```

### 初始化钩子
```bash
./scripts/hooks/init.sh
```

---

## 📝 记忆系统

会话记忆保存在 `memory/` 目录:
- `hooks.log` - 钩子执行日志
- `completed-tasks.md` - 已完成任务
- `ci-history.md` - CI/CD 历史
- `YYYY-MM-DD-*.md` - 每日会话记录

---

## 🆘 故障排除

### 测试失败
```bash
# 运行测试
cd backend
pytest -xvs

# 检查覆盖率
pytest --cov=src --cov-report=html
```

### 类型错误
```bash
cd backend
mypy src
```

### 数据库迁移
```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

---

## 💡 提示

- 每次迭代完成后更新 PROJECT_STATE.md
- 任务完成后运行钩子自动更新状态
- 提交前确保 CI 通过
- 复杂功能先写测试再实现

---

**最后更新**: 2026-02-14  
**维护者**: Tagilla 🤖
