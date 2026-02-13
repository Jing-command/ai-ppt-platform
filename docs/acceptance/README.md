# 验收标准总览

**项目**: AI PPT Platform  
**版本**: 2.0 (优化版)  
**最后更新**: 2026-02-13

---

## 🎯 快速导航

| 优先级 | 数量 | 状态 | 文档 |
|--------|------|------|------|
| 🔴 **MUST** | 30 项 | 待验收 | [查看详情](criteria/00-master-checklist.md) |
| 🟡 **SHOULD** | 50 项 | 待验收 | [查看详情](criteria/) |
| 🟢 **COULD** | 70 项 | 待验收 | [查看详情](criteria/) |

---

## ⚡ 一键检查

```bash
# 运行所有自动化检查
./scripts/acceptance-check.sh

# 查看当前状态
python docs/acceptance/automated/status-report.py
```

---

## 📊 总体进度

```
总体: [░░░░░░░░░░] 0% (0/150)
🔴 MUST:  [░░░░░░░░░░] 0% (0/30)
🟡 SHOULD: [░░░░░░░░░░] 0% (0/50)
🟢 COULD:  [░░░░░░░░░░] 0% (0/70)
```

---

## 🔴 MUST 清单 (30 项)

### 通用要求 (5 项)
- [ ] API P95 响应时间 < 500ms
- [ ] 单元测试行覆盖率 ≥ 80%
- [ ] 无高危安全漏洞 (bandit/sempgrep)
- [ ] 所有 API 有错误处理
- [ ] 核心功能 e2e 测试通过

### 迭代 1: 用户认证 (6 项)
- [ ] 密码使用 bcrypt 加密 (cost >= 12)
- [ ] JWT 使用 HS256, secret >= 256 位
- [ ] 邮箱唯一性验证
- [ ] Token 自动刷新机制
- [ ] API 限流 (登录 5次/分钟)
- [ ] CORS 配置正确

### 迭代 2: 连接器 (5 项)
- [ ] 支持 MySQL 8.0+
- [ ] 凭证 AES-256 加密存储
- [ ] 数据库连接使用 SSL/TLS
- [ ] SQL 参数化查询 (防注入)
- [ ] 连接超时处理 (10秒)

### 迭代 3: 大纲 + AI (5 项)
- [ ] AI 生成响应时间 <= 60 秒
- [ ] 异步任务状态查询
- [ ] 大纲结构正确保存
- [ ] 支持拖拽排序
- [ ] 配图提示词生成

### 迭代 4: PPT 编辑器 (5 项)
- [ ] 撤销/重做支持 50 步
- [ ] 4 套主题正确应用
- [ ] 幻灯片可拖拽排序
- [ ] 文本/图片编辑功能
- [ ] 自动保存草稿

### 迭代 5: 导出系统 (4 项)
- [ ] PPTX 导出可编辑
- [ ] PDF 导出高清
- [ ] 异步导出进度显示
- [ ] 文件 24 小时有效期

---

## 📋 迭代详情

| 迭代 | 功能 | MUST | 详情 |
|------|------|------|------|
| 1 | 用户认证 | 6 项 | [查看](criteria/01-authentication.md) |
| 2 | 连接器管理 | 5 项 | [查看](criteria/02-connectors.md) |
| 3 | 大纲编辑器 | 5 项 | [查看](criteria/03-outlines.md) |
| 4 | PPT 编辑器 | 5 项 | [查看](criteria/04-editor.md) |
| 5 | 导出系统 | 4 项 | [查看](criteria/05-exports.md) |

---

## 🛠️ 工具脚本

| 脚本 | 功能 | 位置 |
|------|------|------|
| `acceptance-check.sh` | 一键运行所有检查 | `scripts/` |
| `status-report.py` | 生成状态报告 | `docs/acceptance/automated/` |
| `update-status.py` | 更新验收状态 | `docs/acceptance/automated/` |

---

## 📁 文件结构

```
docs/acceptance/
├── README.md                    # 本文件 (总览)
├── criteria/                    # 分层标准
│   ├── 00-master-checklist.md   # 主清单 (MUST only)
│   ├── 01-authentication.md     # 迭代1 详情
│   ├── 02-connectors.md         # 迭代2 详情
│   ├── 03-outlines.md           # 迭代3 详情
│   ├── 04-editor.md             # 迭代4 详情
│   └── 05-exports.md            # 迭代5 详情
├── automated/                   # 自动化检查
│   ├── checks.yml               # 检查配置
│   ├── run-checks.py            # 执行检查
│   └── status-report.py         # 状态报告
├── status/                      # 验收状态
│   └── status.json              # 当前状态
└── templates/                   # 模板
    ├── subagent-checklist.md    # Sub-agent 快速清单
    └── release-checklist.md     # 发布清单
```

---

## 🚀 验收流程

```
1. Sub-agent 开发完成
        ↓
2. 运行 ./scripts/acceptance-check.sh
        ↓
3. 检查 🔴 MUST 是否全部通过
        ↓
4. 更新状态: python docs/acceptance/automated/update-status.py
        ↓
5. 提交验收报告
```

---

## 📝 状态文件

验收状态保存在: `docs/acceptance/status/status.json`

查看状态:
```bash
python docs/acceptance/automated/status-report.py
```

---

**注意**: 本目录是优化后的验收标准，原 `ACCEPTANCE_CRITERIA.md` 已归档。
