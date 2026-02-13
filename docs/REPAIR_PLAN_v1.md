# 🔧 修复计划 v1.0

**制定日期**: 2026-02-13  
**制定者**: QA Engineer  
**目标**: 解决验收发现的关键问题，建立长期开发规范

---

## 📊 问题总览

| 优先级 | 问题 | 责任方 | 预计工时 | 截止日期 |
|--------|------|--------|----------|----------|
| 🔴 P0 | 测试覆盖率 < 5% → 目标 80% | Backend/Frontend | 3天 | 2026-02-16 |
| 🔴 P0 | JWT Secret 硬编码风险 | Backend | 0.5天 | 2026-02-14 |
| 🟡 P1 | 缺少 E2E 测试框架 | Frontend | 2天 | 2026-02-18 |
| 🟡 P1 | ESLint 未执行 | Frontend | 0.5天 | 2026-02-14 |
| 🟢 P2 | 性能基准测试 | Backend | 1天 | 2026-02-19 |

---

## 🔴 P0 - 最高优先级 (阻塞上线)

### BE-001: 测试覆盖率提升至 80%

**问题**: 当前覆盖率 < 5%，仅 1 个测试文件

**Backend Agent 任务**:
```
1. 为所有 Service 层编写单元测试
   - auth_service (用户认证)
   - connector_service (连接器)
   - outline_service (大纲)
   - presentation_service (演示文稿)
   - export_service (导出)

2. 为所有 API 端点编写集成测试
   - /api/v1/auth/*
   - /api/v1/connectors/*
   - /api/v1/outlines/*
   - /api/v1/presentations/*
   - /api/v1/exports/*

3. 关键测试场景:
   - 正常流程测试
   - 边界条件测试
   - 错误处理测试
   - 并发测试
```

**Frontend Agent 任务**:
```
1. 组件测试 (React Testing Library)
   - LoginForm
   - ConnectorCard
   - OutlineEditor
   - SlideEditor
   - ExportButton

2. API 客户端测试
   - 所有 API 调用
   - 错误处理
   - Token 刷新

3. E2E 测试 (Playwright/Cypress)
   - 用户注册/登录流程
   - 创建大纲 → 生成 PPT → 导出
   - 连接器配置流程
```

**验收标准**:
- Backend: `pytest --cov=src` ≥ 80%
- Frontend: `jest --coverage` ≥ 80%

---

### BE-002: JWT Secret 安全修复

**问题**: JWT Secret 可能硬编码在代码中

**Backend Agent 任务**:
```
1. 检查所有 JWT Secret 使用位置
2. 移至环境变量 (.env)
3. 更新配置文件
4. 添加 .env.example 模板
5. 更新部署文档
```

**代码示例**:
```python
# 修复前 (不安全)
SECRET_KEY = "hardcoded-secret"

# 修复后 (安全)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not set")
```

---

## 🟡 P1 - 高优先级 (影响质量)

### FE-001: 配置并执行 ESLint

**Frontend Agent 任务**:
```
1. 修复现有 ESLint 错误
   npm run lint --fix

2. 配置 pre-commit hook
   - 提交前自动检查
   - 阻止不合规代码提交

3. 添加 CI 检查
   - GitHub Actions 自动检查
   - PR 时显示检查结果
```

---

### FE-002: E2E 测试框架搭建

**Frontend Agent 任务**:
```
1. 安装 Playwright
   npm install -D @playwright/test

2. 编写核心流程测试:
   - auth.spec.ts (认证流程)
   - outline.spec.ts (大纲流程)
   - editor.spec.ts (编辑器流程)
   - export.spec.ts (导出流程)

3. 配置 CI 自动运行
```

---

## 🟢 P2 - 中优先级 (优化体验)

### BE-003: 性能基准测试

**Backend Agent 任务**:
```
1. 安装性能测试工具
   pip install locust

2. 编写性能测试脚本:
   - API 响应时间测试
   - 并发用户测试 (100 QPS)
   - 数据库查询优化

3. 建立性能基准:
   - P95 响应时间 < 500ms
   - 错误率 < 1%
```

---

## 📝 编写心得规范

### Backend Agent 心得模板

每次提交代码后，在 `docs/dev-notes/backend/` 创建心得：

```markdown
## 开发心得 - [日期]

### 本次任务
- 任务编号: [如 BE-001]
- 任务描述: [简要描述]
- 耗时: [X 小时]

### 遇到的问题
1. **问题**: [描述]
   **解决**: [方法]
   **耗时**: [X 分钟/小时]

2. ...

### 技术决策
- **决策**: [做了什么选择]
- **原因**: [为什么选择这个方案]
- **备选**: [考虑过哪些其他方案]

### 经验教训
- [经验1]
- [经验2]

### 对项目的建议
- [建议1]
- [建议2]

### 参考资料
- [链接1]
- [链接2]
```

### Frontend Agent 心得模板

```markdown
## 开发心得 - [日期]

### 本次任务
- 任务编号: [如 FE-001]
- 任务描述: [简要描述]
- 耗时: [X 小时]

### 组件/页面
- [组件名]: [用途]

### 遇到的问题
1. **问题**: [描述]
   **解决**: [方法]

### UI/UX 决策
- [决策及原因]

### 性能优化
- [做了哪些优化]

### 经验教训
- [经验总结]
```

---

## 🔄 开发流程规范

### 代码规范 (🔴 强制)

所有代码必须严格遵守 **[全局代码规范](../CODING_STANDARDS.md)**:

**提交前强制检查**:
```bash
# 后端
cd backend
black src/              # 代码格式化
isort src/              # import排序
mypy src/               # 类型检查 (必须0 error)
flake8 src/             # 风格检查 (必须0 warning)
bandit -r src/          # 安全扫描 (必须无HIGH)
pytest --cov=src        # 测试覆盖 (必须≥80%)

# 前端
cd frontend
npm run lint            # ESLint (必须0 error)
npm run type-check      # TypeScript (必须0 error)
npm run build           # 构建 (必须成功)
```

**任何检查失败，代码不得提交！**

### 开发流程
1. 接收任务
   ↓
2. 阅读相关文档
   - API 契约
   - 验收标准
   - 之前的心得
   ↓
3. 开发实现
   ↓
4. 自测
   - 单元测试
   - 集成测试
   - 手动测试
   ↓
5. 编写心得
   ↓
6. 提交代码
   ↓
7. QA Engineer 验收
   ↓
8. 修复问题 (如有)
   ↓
9. 完成
```

---

## 📁 文件结构

```
docs/
├── dev-notes/              # 开发心得
│   ├── backend/            # 后端心得
│   │   └── YYYYMMDD-任务号.md
│   └── frontend/           # 前端心得
│       └── YYYYMMDD-任务号.md
├── acceptance/
│   ├── insights/           # QA 心得
│   └── reports/            # 验收报告
```

---

## 🎯 当前 Sprint (2周)

### Week 1 (2.13 - 2.19)

**Backend Agent**:
- [ ] BE-002: JWT Secret 修复 (0.5天)
- [ ] BE-001: 核心 Service 单元测试 (3天)
- [ ] 编写心得: 2-3篇

**Frontend Agent**:
- [ ] FE-001: ESLint 修复 (0.5天)
- [ ] FE-002: E2E 框架搭建 (2天)
- [ ] 编写心得: 2-3篇

**QA Engineer**:
- [ ] 审查 PR
- [ ] 验证修复
- [ ] 更新验收标准

### Week 2 (2.20 - 2.26)

**Backend Agent**:
- [ ] API 集成测试
- [ ] 性能基准测试
- [ ] 迭代 3 功能开发

**Frontend Agent**:
- [ ] E2E 测试用例编写
- [ ] 迭代 3 功能开发

**QA Engineer**:
- [ ] 全面验收
- [ ] 生成质量报告

---

## 📊 成功指标

| 指标 | 当前 | 目标 | 检查方式 |
|------|------|------|----------|
| 测试覆盖率 | <5% | ≥80% | pytest --cov |
| ESLint 错误 | 未知 | 0 | eslint |
| E2E 测试 | 0 | ≥5 个流程 | playwright |
| 安全漏洞 | 1+ | 0 | bandit |
| 开发心得 | 0 | 每周2-3篇 | 文件计数 |

---

## 🚀 启动长期 Sub-agent

### Backend Agent (生命周期: 项目全程)

**职责**:
1. 所有后端功能开发
2. 编写单元测试和集成测试
3. 维护 API 文档
4. 编写开发心得

**交付物**:
- Python 代码
- 测试代码
- 开发心得文档

### Frontend Agent (生命周期: 项目全程)

**职责**:
1. 所有前端功能开发
2. 编写组件测试和 E2E 测试
3. 维护组件文档
4. 编写开发心得

**交付物**:
- TypeScript/React 代码
- 测试代码
- 开发心得文档

### QA Engineer Agent (生命周期: 项目全程)

**职责**:
1. 定期验收
2. 生成质量报告
3. 提出改进建议
4. 维护验收标准

**交付物**:
- 验收报告
- 心得体会
- 流程优化建议

---

**修复计划已制定，准备启动长期 Sub-agent！**
