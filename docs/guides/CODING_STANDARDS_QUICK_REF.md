# 🎯 AI PPT Platform - 代码规范速查卡

**全局规范**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS.md`  
**强制性条款**: `/root/.openclaw/workspace/.openclaw/standards/MANDATORY_CLAUSE.md`  
**全局速查卡**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS_QUICK_REF.md`

---

## 🚀 提交前必做 (30秒检查)

```bash
# ========== 后端 ==========
cd backend
black src/             # 格式化
isort src/             # import排序
mypy src/              # 必须 0 error
flake8 src/            # 必须 0 warning
bandit -r src/         # 必须无高危
pytest --cov=src       # 必须 ≥ 80%

# ========== 前端 ==========
cd frontend
npm run lint           # 必须 0 error
npm run type-check     # 必须 0 error
npm run build          # 必须成功
```

---

## 📝 命名速查

| 类型 | 规范 | 示例 |
|------|------|------|
| **常量** | `SCREAMING_SNAKE_CASE` | `MAX_RETRY = 3` |
| **变量** | `camelCase` (TS) / `snake_case` (Python) | `userName` / `user_name` |
| **函数** | `camelCase` (TS) / `snake_case` (Python) | `getUserById()` / `get_user_by_id()` |
| **类/接口** | `PascalCase` | `UserService` |
| **私有** | `_leadingUnderscore` | `_internal_method()` |
| **CSS 类** | `BEM` 命名 | `.user-card__title--large` |

---

## 🔒 安全红线 (绝不能犯)

```python
# ❌ SQL 注入 - 禁止
f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))


# ❌ 命令注入 - 禁止
os.system(f"ping {host}")

# ✅ 安全执行
subprocess.run(["ping", host])
```

```typescript
// ❌ XSS - 禁止
element.innerHTML = userInput;

// ✅ 安全插入
element.textContent = userInput;
```

```python
# ❌ 硬编码密钥 - 禁止
JWT_SECRET = "my-secret-key"

# ✅ 环境变量
JWT_SECRET = os.environ.get("JWT_SECRET_KEY")
```

---

## 🎨 CSS 属性顺序 (AlloyTeam)

```css
.element {
  /* 1. 布局 */
  display, visibility, float, clear, overflow
  
  /* 2. 定位 */
  position, top, right, bottom, left, z-index
  
  /* 3. 盒模型 */
  margin, border, padding, width, height
  
  /* 4. 字体 */
  font, line-height, text-align
  
  /* 5. 视觉 */
  color, background, opacity
  
  /* 6. 动画 */
  transition, transform, animation
}
```

---

## ✅ 代码审查清单

### 提交前自检
- [ ] 代码通过 lint 检查
- [ ] 类型检查无错误
- [ ] 单元测试全部通过
- [ ] 新增代码覆盖率 ≥ 80%
- [ ] 安全扫描无高危
- [ ] 无敏感信息硬编码
- [ ] 注释清晰完整

### 审查重点
| 检查项 | 优先级 |
|--------|--------|
| 安全漏洞 | 🔴 P0 |
| 测试覆盖 | 🔴 P0 |
| 代码风格 | 🟡 P1 |
| 类型安全 | 🟡 P1 |

---

## 🛠️ 快速修复命令

```bash
# 后端格式化
black src/
isort src/

# 前端修复
npm run lint -- --fix

# 类型检查修复
# 根据 mypy/npm 输出逐一修复
```

---

## 📚 参考

- **全局规范**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS.md`
- **强制性条款**: `/root/.openclaw/workspace/.openclaw/standards/MANDATORY_CLAUSE.md`
- **全局速查卡**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS_QUICK_REF.md`
- **腾讯 secguide**: https://github.com/Tencent/secguide
- **AlloyTeam**: https://alloyteam.github.io/CodeGuide/

---

**记住**: 写出诗一样的代码 🎨
