# 登录功能实现

## 项目结构

```
my-app/
├── app/
│   ├── login/
│   │   └── page.tsx          # 登录页面
│   └── dashboard/
│       └── page.tsx          # 仪表盘页面（登录后跳转）
├── components/
│   └── auth/
│       └── LoginForm.tsx     # 登录表单组件（可复用）
├── lib/
│   └── api/
│       ├── client.ts         # Axios 配置
│       └── auth.ts           # 认证相关 API
├── types/
│   └── auth.ts               # TypeScript 类型定义
├── next.config.js            # Next.js 配置
├── package.json              # 项目依赖
└── tsconfig.json             # TypeScript 配置
```

## 安装依赖

```bash
cd my-app
npm install
```

## 运行开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

## 登录流程

1. 用户访问 `http://localhost:3000/login`
2. 输入邮箱和密码
3. 表单验证通过 Zod schema 进行验证
4. 点击登录按钮，调用 `POST /api/v1/auth/login`
5. 登录成功：
   - 保存 `accessToken` 到 localStorage
   - 保存用户信息到 localStorage
   - 跳转到 `/dashboard`
6. 登录失败：
   - 显示对应的错误提示

## API 错误处理

| 状态码 | 错误提示 |
|--------|----------|
| 401 | 邮箱或密码错误 |
| 422 | 表单验证错误，请检查输入 |
| 500 | 服务器错误，请稍后重试 |
| 其他 | 登录失败，请稍后重试 |

## 环境变量

可以在项目根目录创建 `.env.local` 文件来配置 API 地址：

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

如果不配置，默认使用 `http://localhost:8000/api/v1`。

## 测试登录功能

1. 确保后端服务运行在 `http://localhost:8000`
2. 启动前端：`npm run dev`
3. 访问 `http://localhost:3000/login`
4. 使用有效的用户凭证登录

## 特性

- ✅ React Hook Form 表单管理
- ✅ Zod 表单验证
- ✅ TypeScript 严格模式
- ✅ 加载状态显示（spinner）
- ✅ 错误处理与提示
- ✅ 响应式设计
- ✅ Token 自动添加到请求头
- ✅ 路由保护（未登录跳转到登录页）
