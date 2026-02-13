# Sub-agent 快速验收清单

**使用场景**: Sub-agent 完成开发后快速自检  
**检查时间**: 5-10 分钟  
**通过标准**: 所有 🔴 MUST 项通过

---

## 🚀 快速开始

```bash
# 1. 运行自动化检查
./scripts/acceptance-check.sh --must-only

# 2. 查看当前状态
python docs/acceptance/automated/status-report.py

# 3. 更新通过的项
python docs/acceptance/automated/update-status.py --item AUTH-01 --status passed
```

---

## 🔴 MUST 清单 (30项核心)

### 开发前必须阅读
- [ ] 已阅读 `docs/acceptance/criteria/00-master-checklist.md`
- [ ] 已阅读对应迭代的详细验收标准
- [ ] 已阅读 `docs/architecture/API_CONTRACT.md`

### 代码质量 (5项)
- [ ] `pytest` 测试通过率 100%
- [ ] 测试覆盖率 ≥ 80% (`pytest --cov`)
- [ ] `eslint` 无错误 (`eslint . --quiet`)
- [ ] `bandit` 无高危漏洞 (`bandit -r src/`)
- [ ] `mypy` 类型检查通过 (`mypy src/`)

### API 规范 (5项)
- [ ] 所有端点以 `/api/v1/` 开头
- [ ] 包含版本号 (如 `/api/v1/`)
- [ ] 使用正确的 HTTP 方法 (GET/POST/PUT/DELETE)
- [ ] 响应格式符合统一标准
- [ ] 包含完整的错误处理

### 安全要求 (5项)
- [ ] 密码使用 bcrypt 加密
- [ ] JWT Secret 长度 ≥ 256 位
- [ ] 数据库连接使用 SSL/TLS
- [ ] SQL 查询使用参数化 (防注入)
- [ ] API 限流已配置

### 性能要求 (5项)
- [ ] API P95 响应时间 < 500ms
- [ ] 数据库查询 < 100ms
- [ ] 静态资源已缓存
- [ ] 无 N+1 查询问题
- [ ] 内存使用合理

### 功能完整 (5项)
- [ ] 所有 API 端点已实现
- [ ] 前端页面可正常访问
- [ ] 核心功能流程可走完
- [ ] 错误提示友好
- [ ] 边界情况已处理

### 文档要求 (5项)
- [ ] API 文档已更新 (Swagger)
- [ ] 复杂逻辑有注释
- [ ] 配置文件有示例
- [ ] README 已更新 (如需要)
- [ ] 变更已记录

---

## 🛠️ 一键检查命令

```bash
#!/bin/bash
# 保存为 check-my-work.sh

echo "🔍 开始验收检查..."

# 后端检查
cd backend
source venv/bin/activate 2>/dev/null || true

echo ""
echo "1. 运行测试..."
pytest --tb=short -q

echo ""
echo "2. 检查覆盖率..."
pytest --cov=src --cov-report=term-missing -q

echo ""
echo "3. 类型检查..."
mypy src/ || true

echo ""
echo "4. 安全扫描..."
bandit -r src/ -f json -o /tmp/bandit.json || true
if grep -q '"issue_severity": "HIGH"' /tmp/bandit.json 2>/dev/null; then
    echo "❌ 发现高危漏洞!"
    cat /tmp/bandit.json | grep -A5 '"issue_severity": "HIGH"'
else
    echo "✅ 无高危漏洞"
fi

cd ..

# 前端检查
cd frontend

echo ""
echo "5. 前端代码检查..."
npm run lint 2>/dev/null || eslint . --ext .ts,.tsx --quiet

cd ..

echo ""
echo "✅ 检查完成!"
```

---

## 📊 验收流程

```
开发完成
    ↓
自检 (本清单)
    ↓
运行自动化检查
    ↓
修复问题
    ↓
更新状态文件
    ↓
提交验收报告
```

---

## 🆘 常见问题

### Q: 测试覆盖率不足 80% 怎么办？
```bash
# 查看未覆盖的代码
pytest --cov=src --cov-report=html
cd htmlcov && python -m http.server 8080
# 打开浏览器查看，补充测试用例
```

### Q: 发现高危安全漏洞怎么办？
```bash
# 查看详细信息
bandit -r src/ -v

# 常见修复:
# - 使用参数化查询防 SQL 注入
# - 使用 bcrypt 替代明文密码
# - 验证所有用户输入
```

### Q: API 响应慢怎么办？
```bash
# 使用 py-spy 或 cProfile 分析
python -m cProfile -o profile.stats -m pytest tests/
python -m pstats profile.stats
```

---

## 📝 验收报告模板

```markdown
## 验收报告

**迭代**: [1/2/3/4/5]  
**功能**: [功能名称]  
**开发**: [Sub-agent ID]  
**日期**: [日期]

### 检查结果

| 类别 | 状态 | 备注 |
|------|------|------|
| 代码质量 | ✅/❌ | |
| API 规范 | ✅/❌ | |
| 安全要求 | ✅/❌ | |
| 性能要求 | ✅/❌ | |
| 功能完整 | ✅/❌ | |
| 文档要求 | ✅/❌ | |

### 通过的 MUST 项
- [ ] ITEM-01
- [ ] ITEM-02
...

### 失败项及原因
- ITEM-XX: [原因]

### 证据
- 测试报告: [链接]
- 覆盖率报告: [链接]
- 代码审查: [链接]

### 结论
✅ 通过 / ❌ 不通过
```

---

## 🎯 通过标准

**必须全部满足**:
1. 30 项 MUST 全部通过
2. 自动化检查无错误
3. 代码审查通过

**可接受**:
- 最多 3 项 SHOULD 失败
- 性能指标在 110% 以内

---

**记住**: 
- 🔴 MUST = 必须全部通过
- 🟡 SHOULD = 强烈建议
- 🟢 COULD = 有更好，没有也行

**有问题？** 查看详细标准: `docs/acceptance/criteria/`
