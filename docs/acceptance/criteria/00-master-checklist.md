# 🔴 MUST 清单 - 必须通过项

**文档**: Master Checklist  
**范围**: 所有 MUST (必须有) 级别验收项  
**总计**: 30 项

---

## ✅ 验收状态

```
总体进度: [░░░░░░░░░░] 0% (0/30)
```

---

## 通用要求 (10 项)

| # | 检查项 | 标准 | 检查命令 | 状态 |
|---|--------|------|----------|------|
| G-01 | API 响应时间 | P95 < 500ms | `k6 run load-test.js` | ⬜ |
| G-02 | 测试覆盖率 | 行覆盖 ≥ 80% | `pytest --cov=src` | ⬜ |
| G-03 | 安全漏洞 | 无高危漏洞 | `bandit -r src/` | ⬜ |
| G-04 | 错误处理 | 所有 API 有错误处理 | 代码审查 | ⬜ |
| G-05 | E2E 测试 | 核心功能通过 | `pytest tests/e2e/` | ⬜ |

## 代码规范要求 (5 项) 🔴

**参考文档**: [全局代码规范](../../CODING_STANDARDS.md)

| # | 检查项 | 标准 | 检查命令 | 状态 |
|---|--------|------|----------|------|
| CODE-01 | 前端代码规范 | ESLint 零错误 | `npm run lint` | ⬜ |
| CODE-02 | 前端类型安全 | TypeScript 零错误 | `npm run type-check` | ⬜ |
| CODE-03 | 后端代码规范 | Black + isort 格式化 | `black src/ && isort src/` | ⬜ |
| CODE-04 | 后端类型检查 | mypy 零错误 | `mypy src/` | ⬜ |
| CODE-05 | 代码风格检查 | flake8 无警告 | `flake8 src/` | ⬜ |

---

## 迭代 1: 用户认证 (6 项)

| # | 检查项 | 标准 | 检查方法 | 状态 |
|---|--------|------|----------|------|
| AUTH-01 | 密码加密 | bcrypt, cost ≥ 12 | 代码审查 `core/security.py` | ⬜ |
| AUTH-02 | JWT 算法 | HS256, secret ≥ 256位 | 环境变量检查 | ⬜ |
| AUTH-03 | 邮箱唯一性 | 注册时验证 | 测试用例 | ⬜ |
| AUTH-04 | Token 刷新 | 自动刷新机制 | 功能测试 | ⬜ |
| AUTH-05 | API 限流 | 登录 5次/分钟 | 压力测试 | ⬜ |
| AUTH-06 | CORS 配置 | 白名单正确 | 配置审查 | ⬜ |

**API 端点**:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

---

## 迭代 2: 连接器管理 (5 项)

| # | 检查项 | 标准 | 检查方法 | 状态 |
|---|--------|------|----------|------|
| CONN-01 | MySQL 支持 | MySQL 8.0+ | 功能测试 | ⬜ |
| CONN-02 | 凭证加密 | AES-256 | 代码审查 | ⬜ |
| CONN-03 | SSL/TLS | 强制加密连接 | 配置检查 | ⬜ |
| CONN-04 | SQL 注入防护 | 参数化查询 | 代码审查 + SQLMap | ⬜ |
| CONN-05 | 连接超时 | 10 秒超时 | 功能测试 | ⬜ |

**API 端点**:
- `GET /api/v1/connectors`
- `POST /api/v1/connectors`
- `POST /api/v1/connectors/{id}/test`
- `POST /api/v1/connectors/{id}/query`

---

## 迭代 3: 大纲编辑器 (5 项)

| # | 检查项 | 标准 | 检查方法 | 状态 |
|---|--------|------|----------|------|
| OUT-01 | AI 生成时间 | ≤ 60 秒 | 计时测试 | ⬜ |
| OUT-02 | 异步任务 | 状态可查询 | 功能测试 | ⬜ |
| OUT-03 | 大纲保存 | 结构正确 | 单元测试 | ⬜ |
| OUT-04 | 拖拽排序 | 章节可排序 | E2E 测试 | ⬜ |
| OUT-05 | 配图提示词 | 每页生成提示词 | 功能测试 | ⬜ |

**API 端点**:
- `GET /api/v1/outlines`
- `POST /api/v1/outlines/generate`
- `GET /api/v1/outlines/generate/{task_id}/status`
- `PUT /api/v1/outlines/{id}`

---

## 迭代 4: PPT 编辑器 (5 项)

| # | 检查项 | 标准 | 检查方法 | 状态 |
|---|--------|------|----------|------|
| EDT-01 | 撤销重做 | 50 步历史 | 功能测试 | ⬜ |
| EDT-02 | 主题应用 | 4 套主题正常 | 视觉测试 | ⬜ |
| EDT-03 | 幻灯片排序 | 可拖拽排序 | E2E 测试 | ⬜ |
| EDT-04 | 编辑功能 | 文本/图片可编辑 | 功能测试 | ⬜ |
| EDT-05 | 自动保存 | 草稿自动保存 | 功能测试 | ⬜ |

**API 端点**:
- `GET /api/v1/presentations/{id}/slides`
- `PUT /api/v1/presentations/{id}/slides/{slide_id}`
- `POST /api/v1/presentations/{id}/undo`
- `POST /api/v1/presentations/{id}/redo`

---

## 迭代 5: 导出系统 (4 项)

| # | 检查项 | 标准 | 检查方法 | 状态 |
|---|--------|------|----------|------|
| EXP-01 | PPTX 质量 | 可编辑,主题正确 | 人工检查 | ⬜ |
| EXP-02 | PDF 质量 | 高清, 可选中文本 | 人工检查 | ⬜ |
| EXP-03 | 进度显示 | 实时进度条 | 功能测试 | ⬜ |
| EXP-04 | 文件有效期 | 24 小时 | 自动化测试 | ⬜ |

**API 端点**:
- `POST /api/v1/exports/pptx`
- `POST /api/v1/exports/pdf`
- `POST /api/v1/exports/images`
- `GET /api/v1/exports/{task_id}/status`

---

## 🛠️ 验收命令

### 快速检查所有 MUST
```bash
./scripts/acceptance-check.sh --must-only
```

### 检查单个迭代
```bash
./scripts/acceptance-check.sh --iteration 1  # 用户认证
./scripts/acceptance-check.sh --iteration 2  # 连接器
```

### 更新状态
```bash
python docs/acceptance/automated/update-status.py --item AUTH-01 --status PASSED
```

---

## 📊 验收标准

**通过条件**:
- ✅ 35 项 MUST 全部通过 (30 原项 + 5 代码规范)
- ✅ 无高危安全漏洞
- ✅ E2E 测试通过率 100%
- ✅ 代码规范检查全部通过

**有条件通过**:
- 🟡 最多 3 项 SHOULD 失败
- 🟡 性能指标在 110% 以内

**不通过**:
- ❌ 任何 MUST 项失败 (包括代码规范)
- ❌ 发现高危安全漏洞
- ❌ 核心功能不可用
- ❌ 代码规范检查未通过

---

## 📝 状态追踪

实时状态查看:
```bash
python docs/acceptance/automated/status-report.py
```

输出示例:
```
🔴 MUST 进度: 25/30 (83%)
✅ 已通过: 25
❌ 失败: 0
⬜ 待测试: 5

最近通过:
- AUTH-01: 密码加密 (2分钟前)
- AUTH-02: JWT 算法 (5分钟前)
```

---

**上次更新**: 2026-02-13  
**下次审查**: 每个迭代完成后
