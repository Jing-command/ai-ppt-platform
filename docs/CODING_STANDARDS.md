# 📘 AI PPT Platform - 代码规范

**规范来源**: OpenClaw 全局代码规范  
**全局规范路径**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS.md`  
**速查卡**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS_QUICK_REF.md`

---

## 🎯 项目专用补充规范

本文件是对全局代码规范的补充说明，**所有通用规范以全局规范为准**。

---

## 📁 项目结构规范

### 后端结构

```
backend/
├── src/ai_ppt/
│   ├── api/              # API 端点 (v1/endpoints/)
│   ├── services/         # 业务逻辑
│   ├── models/           # 数据库模型
│   ├── domain/           # 领域模型
│   ├── core/             # 核心配置 (安全、配置)
│   └── infrastructure/   # 基础设施 (数据库、缓存)
├── tests/
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
└── alembic/              # 数据库迁移
```

### 前端结构

```
frontend/
├── app/                  # Next.js App Router
│   ├── (auth)/           # 认证相关页面 (路由分组)
│   ├── (dashboard)/      # 主控制台页面
│   └── api/              # API Routes
├── components/
│   ├── auth/             # 认证组件
│   ├── outlines/         # 大纲编辑器组件
│   ├── presentations/    # PPT 编辑器组件
│   └── ui/               # 通用 UI 组件
├── lib/
│   ├── api/              # API 客户端
│   └── utils/            # 工具函数
├── hooks/                # 自定义 Hooks
└── types/                # TypeScript 类型
```

---

## 🔐 项目专用安全规范

### JWT 配置

```python
# config.py
JWT_SECRET_KEY: str  # 必须在环境变量中设置，无默认值
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

### 数据库凭证加密

```python
# 连接器凭证使用 AES-256 加密
from cryptography.fernet import Fernet

encryption_key = os.environ.get("DB_ENCRYPTION_KEY")
cipher = Fernet(encryption_key)
encrypted_password = cipher.encrypt(password.encode())
```

---

## 🧪 项目测试规范

### 测试文件命名

```
tests/
├── unit/
│   ├── test_auth_service.py      # 服务层单元测试
│   ├── test_connector_service.py
│   └── test_outline_service.py
└── integration/
    ├── test_auth_api.py          # API 集成测试
    └── test_connector_api.py
```

### 测试覆盖率要求

| 模块 | 最低覆盖率 |
|------|-----------|
| services/ | 90% |
| api/endpoints/ | 85% |
| models/ | 80% |
| core/ | 95% |
| **整体** | **≥ 80%** |

---

## 📐 API 设计规范

### 响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2026-02-13T19:30:00Z"
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "请求参数错误",
  "errors": [
    { "field": "email", "message": "邮箱格式不正确" }
  ],
  "timestamp": "2026-02-13T19:30:00Z"
}
```

---

## 🎨 项目 UI 规范

### 颜色系统

```typescript
// Tailwind 配置
colors: {
  primary: {
    50: '#e6f7ff',
    500: '#1890ff',
    600: '#096dd9',
  },
  danger: '#ff4d4f',
  success: '#52c41a',
  warning: '#faad14',
}
```

### 间距系统

```typescript
// 基于 8px 栅格
spacing: {
  'xs': '4px',
  'sm': '8px',
  'md': '16px',
  'lg': '24px',
  'xl': '32px',
  '2xl': '48px',
}
```

---

## ✅ 提交前检查清单

```bash
# ========== 后端 ==========
cd backend
black src/
isort src/
mypy src/
flake8 src/
bandit -r src/
pytest --cov=src --cov-report=term-missing

# ========== 前端 ==========
cd frontend
npm run lint
npm run type-check
npm run build
```

**任何检查失败，代码不得提交！**

---

## 📚 参考

- **全局规范**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS.md`
- **速查卡**: `/root/.openclaw/workspace/.openclaw/standards/CODING_STANDARDS_QUICK_REF.md`
- **腾讯 secguide**: https://github.com/Tencent/secguide
- **AlloyTeam**: https://alloyteam.github.io/CodeGuide/

---

**生效日期**: 2026-02-13  
**规范版本**: 1.0.0
