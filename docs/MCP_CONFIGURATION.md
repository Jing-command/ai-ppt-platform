# MCP 服务器配置文档

**文档版本**: 1.0  
**创建日期**: 2026-02-13  
**适用项目**: AI PPT Platform

---

## 📦 已安装的 MCP 服务

### 1. GitHub MCP ⭐

**包名**: `@modelcontextprotocol/server-github`

**功能**:
- 创建/查看 Pull Request
- 管理 Issues
- 查看代码提交历史
- 创建分支和标签
- 仓库文件操作

**配置方法**:

```bash
# 1. 获取 GitHub Token
# 访问: https://github.com/settings/tokens
# 勾选权限: repo, read:user, read:org

# 2. 设置环境变量
export GITHUB_TOKEN=ghp_your_github_token_here

# 3. 启动 MCP 服务器
npx @modelcontextprotocol/server-github
```

**使用示例**:
```bash
# 列出用户仓库
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/repos

# 创建 Issue
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"title":"Bug Report","body":"描述问题"}' \
  https://api.github.com/repos/OWNER/REPO/issues
```

**验证状态**: ✅ 已配置（用户: Jing-command）

---

### 2. Puppeteer MCP ⭐

**包名**: `@modelcontextprotocol/server-puppeteer`

**功能**:
- 网页截图 ✅（已验证）
- PDF 生成
- 浏览器自动化
- 页面点击/输入操作
- 爬虫数据采集
- 无头浏览器操作（无需图形界面）

**配置方法**:

```bash
# 1. 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y \
  libasound2t64 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libxss1 libpangocairo-1.0-0 libpango-1.0-0 \
  libcairo2 libgdk-pixbuf2.0-0 libgtk-3-0

# 2. 安装 Puppeteer
npm install -g @modelcontextprotocol/server-puppeteer
# 或本地安装
npm install puppeteer
```

**使用示例**:
```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.goto('https://example.com');
  
  // 截图
  await page.screenshot({ path: 'screenshot.png', fullPage: true });
  
  // 生成 PDF
  await page.pdf({ path: 'page.pdf', format: 'A4' });
  
  await browser.close();
})();
```

**验证状态**: ✅ 截图测试通过（18KB PNG文件已生成）

---

### 3. ESLint MCP（静态代码分析）

**说明**: 不需要 AI API Key，基于规则引擎的代码检查

**安装方法**:

```bash
# ESLint 本身支持 MCP 模式
npm install -g eslint

# 使用 MCP 模式启动
npx eslint --mcp
```

**功能**:
- 语法错误检测
- 代码风格检查
- 潜在问题发现
- 支持 JavaScript/TypeScript

**配置 `.eslintrc.js`**:
```javascript
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'off',
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always']
  }
};
```

**使用示例**:
```bash
# 检查单个文件
npx eslint src/app.js

# 检查整个项目
npx eslint src/

# 自动修复问题
npx eslint src/ --fix

# 输出 JSON 格式（供 AI 分析）
npx eslint src/ --format json
```

**验证状态**: ⏳ 待安装配置

---

## 🔄 已弃用的 MCP

### ~~code-review-mcp~~

**弃用原因**: 需要 OpenAI/Anthropic API Key  
**替代方案**: ESLint MCP（无需 API Key）

---

## 🚀 快速启动命令

```bash
# 1. 设置环境变量
export GITHUB_TOKEN=ghp_your_github_token_here

# 2. 启动 GitHub MCP
npx @modelcontextprotocol/server-github

# 3. 使用 Puppeteer 截图
cd /tmp && node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'screenshot.png' });
  await browser.close();
  console.log('截图完成!');
})();
"

# 4. 代码检查
npx eslint your-project/src/ --format json
```

---

## 📝 使用场景

| 场景 | 推荐 MCP | 命令 |
|------|----------|------|
| 创建 GitHub PR | GitHub MCP | `npx @modelcontextprotocol/server-github` |
| 网页截图 | Puppeteer MCP | `node puppeteer_script.js` |
| 代码质量检查 | ESLint MCP | `npx eslint src/ --fix` |
| 生成 PDF | Puppeteer MCP | `page.pdf({ path: 'doc.pdf' })` |
| 爬虫数据采集 | Puppeteer MCP | `page.goto() + page.evaluate()` |

---

## ⚠️ 注意事项

1. **GitHub Token 安全**
   - 不要硬编码在代码中
   - 使用环境变量传递
   - 定期更换 Token

2. **Puppeteer 依赖**
   - 需要安装系统依赖库（见上方 apt-get 命令）
   - 无头模式不需要图形界面
   - 截图/PDFF功能已验证可用

3. **ESLint 规则**
   - 根据项目需求配置 `.eslintrc.js`
   - 推荐与 Prettier 配合使用
   - 集成到 CI/CD 流程

---

## 🔧 故障排除

### Puppeteer 截图失败

**错误**: `libatk-1.0.so.0: cannot open shared object file`

**解决**:
```bash
sudo apt-get update
sudo apt-get install -y libasound2t64 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libxss1 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
  libgdk-pixbuf2.0-0 libgtk-3-0
```

### GitHub API 401

**检查**:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**解决**: 重新生成 Token，确保有 `repo` 权限

---

## 📚 参考链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [GitHub MCP 仓库](https://github.com/modelcontextprotocol/servers)
- [Puppeteer 文档](https://pptr.dev/)
- [ESLint 配置指南](https://eslint.org/docs/user-guide/configuring)

---

*最后更新: 2026-02-13*  
*维护者: Tagilla*
