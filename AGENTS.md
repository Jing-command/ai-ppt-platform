# 🤖 AI PPT Platform - 快速参考

**状态**: 迭代1-3完成 ✅ | **覆盖率**: 83% | **CI**: 通过

---

## 📊 项目进度

| 模块 | 状态 |
|------|------|
| 用户认证 | ✅ 完成 |
| 连接器管理 | ✅ 完成 |
| PPT核心功能 | ✅ 完成 |
| 导出系统 | ✅ 完成 |
| CI/CD测试 | ✅ 780测试通过 |
| 大纲编辑器 | ⏳ 迭代4待开始 |

---

## 📋 当前任务

查看: `cat task-queue.md`  
更新: `./scripts/hooks/on_task_complete.sh "任务名" success`

---

## 🔌 关键API

- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/presentations` - 创建PPT
- `GET /api/v1/presentations/{id}` - 获取PPT

---

## 🛠️ 开发规范

- Python: `snake_case` + 类型注解
- 测试: pytest, 覆盖率≥80%
- 提交: CI通过后才能合并

---

## 🪝 钩子系统

```bash
./scripts/hooks/on_session_start.sh    # 加载上下文
./scripts/hooks/on_task_complete.sh    # 完成任务
./scripts/hooks/init.sh                # 初始化
```

---

**详细文档**: HOOKS.md | API_CONTRACT.md | PROJECT_STATE.md
