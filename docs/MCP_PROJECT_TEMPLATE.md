# 项目 MCP 配置模板

**每个新项目启动时自动加载**

---

## 🔧 基础 MCP（所有项目可用）

### 1. GitHub MCP
```bash
# 环境变量（需要配置）
export GITHUB_TOKEN=ghp_your_github_token_here

# 快速命令
alias github-mcp='npx @modelcontextprotocol/server-github'
```

**使用场景**:
- 创建 PR/MR
- 管理 Issues
- 代码审查
- 查看提交历史

### 2. Puppeteer MCP
```bash
# 截图命令
alias screenshot='node -e "const p=require(\"puppeteer\");(async()=>{const b=await p.launch({headless:true,args:[\"--no-sandbox\"]});const p=await b.newPage();await p.goto(process.argv[1]);await p.screenshot({path:process.argv[2]});await b.close();})()"'

# PDF 生成
alias pdf-gen='node -e "const p=require(\"puppeteer\");(async()=>{const b=await p.launch({headless:true,args:[\"--no-sandbox\"]});const p=await b.newPage();await p.goto(process.argv[1]);await p.pdf({path:process.argv[2]});await b.close();})()"'
```

**使用场景**:
- 网页截图验证
- 生成 PDF 报告
- 前端自动化测试
- 爬虫数据采集

### 3. ESLint MCP
```bash
# 代码检查
alias lint='npx eslint --fix'
alias lint-check='npx eslint --format json'

# 项目级检查
alias lint-project='npx eslint src/ --ext .js,.jsx,.ts,.tsx'
```

**使用场景**:
- 代码提交前检查
- 代码审查辅助
- 自动修复风格问题

---

## 🤖 自动触发规则

### 当我（Tagilla）看到以下关键词时，**自动**使用对应 MCP：

| 关键词 | 自动触发 MCP | 操作 |
|--------|-------------|------|
| "创建 PR" / "提交代码" | GitHub MCP | 创建 PR、推送代码 |
| "截图" / "测试页面" | Puppeteer MCP | 网页截图、验证效果 |
| "代码质量" / "lint" | ESLint MCP | 检查代码、修复问题 |
| "生成 PDF" / "导出" | Puppeteer MCP | 生成 PDF 报告 |
| "GitHub" / "仓库" | GitHub MCP | 查询仓库信息 |

---

## 👥 Sub Agent 使用规则

### 子代理任务分配时自动携带 MCP 权限：

```yaml
# 子代理任务模板
session_spawn:
  agent: main
  label: "coding-task"
  tools:  # 自动携带
    - github-mcp      # 可创建 PR
    - puppeteer-mcp   # 可截图验证
    - eslint-mcp      # 可检查代码
```

### 子代理在以下情况必须使用 MCP：

1. **完成代码编写后** → 必须用 ESLint 检查
2. **前端页面开发后** → 必须用 Puppeteer 截图验证
3. **需要提交代码时** → 必须用 GitHub MCP 创建 PR
4. **代码审查任务** → 必须用 ESLint + GitHub PR

---

## 📊 MCP 使用监控

### 每次使用 MCP 后记录到 `PROJECT_STATE.md`：

```markdown
## MCP 使用记录
- 2026-02-13: Puppeteer 截图验证大纲编辑页 ✅
- 2026-02-13: GitHub MCP 创建 PR #12 ✅
- 2026-02-13: ESLint 检查 Iteration 4 代码 ✅
```

---

## 🚀 快速启动（每个项目初始化时执行）

```bash
#!/bin/bash
# mcp-init.sh - 新项目 MCP 初始化

echo "=== 初始化项目 MCP 配置 ==="

# 1. 检查环境变量
if [ -z "$GITHUB_TOKEN" ]; then
  echo "⚠️  GITHUB_TOKEN 未设置"
  echo "请运行: export GITHUB_TOKEN=your_token"
fi

# 2. 安装项目级 ESLint 配置
if [ ! -f ".eslintrc.js" ]; then
  echo "创建 ESLint 配置..."
  cat > .eslintrc.js << 'EOF'
module.exports = {
  env: { browser: true, es2021: true, node: true },
  extends: ['eslint:recommended'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'off',
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always']
  }
};
EOF
fi

# 3. 创建截图测试脚本
if [ ! -f "scripts/screenshot.js" ]; then
  mkdir -p scripts
  cat > scripts/screenshot.js << 'EOF'
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ 
    headless: true, 
    args: ['--no-sandbox'] 
  });
  const page = await browser.newPage();
  await page.goto(process.argv[2] || 'http://localhost:3000');
  await page.screenshot({ 
    path: process.argv[3] || 'screenshot.png',
    fullPage: true 
  });
  await browser.close();
  console.log('✅ 截图完成');
})();
EOF
fi

echo "✅ MCP 初始化完成"
echo ""
echo "可用命令:"
echo "  npm run screenshot -- http://localhost:3000" 
echo "  npx eslint src/ --fix"
echo "  git push origin main && gh pr create"
```

---

## 📝 更新记录

| 日期 | 更新内容 | 操作者 |
|------|----------|--------|
| 2026-02-13 | 初始配置 | Tagilla |
| 2026-02-13 | 添加自动触发规则 | Tagilla |

---

*模板版本: 1.0 | 所有新项目自动应用*
