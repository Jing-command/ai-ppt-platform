# 📘 AI PPT Platform - 全局代码规范

**版本**: 1.0.0  
**基于**: 腾讯 AlloyTeam / IMWeb / secguide 规范  
**适用范围**: 所有 Sub-agent 编写代码  
**强制程度**: 🔴 MUST - 必须严格遵守

---

## 🎯 规范理念

> "代码千万行，安全第一行；前端不规范，同事两行泪。"

**核心原则**:
1. **可读性优先** - 代码是写给人看的，顺便给机器执行
2. **安全左移** - 从源头杜绝漏洞，而非事后修补
3. **一致性** - 统一风格，降低认知成本
4. **可维护性** - 方便调试、测试、重构

---

## 📋 规范清单 (快速检查)

```bash
# 前端代码检查
npm run lint              # ESLint 零错误
npm run type-check        # TypeScript 零错误
npm run build             # 构建成功

# 后端代码检查
black src/                # 代码格式化
isort src/                # import 排序
mypy src/                 # 类型检查零错误
flake8 src/               # 代码风格检查
bandit -r src/            # 安全扫描无高危
pytest --cov=src          # 测试覆盖率 ≥ 80%
```

---

## 🎨 前端代码规范

### 1. JavaScript / TypeScript 规范

#### 1.1 命名规范

```typescript
// ✅ 常量 - 全大写下划线
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';

// ✅ 变量 - 驼峰命名
const userName = '张三';
const slideList = [];

// ✅ 类名 - PascalCase
class UserService {}
class SlideEditor {}

// ✅ 接口名 - PascalCase 前缀 I (可选)
interface IUser {
  id: string;
  name: string;
}

// ✅ 类型别名 - PascalCase
type SlideType = 'title' | 'content' | 'image';

// ✅ 函数 - 驼峰命名，动词开头
function getUserById(id: string) {}
function handleSubmit() {}
function isValidEmail(email: string): boolean {}

// ✅ 布尔变量 - is/has/should 前缀
const isLoading = false;
const hasError = true;
const shouldRetry = false;

// ❌ 禁止
const user_name = '';        // 蛇形命名
const userNameList = [];     // 匈牙利命名
const get_user = () => {};   // 蛇形命名
```

#### 1.2 代码格式

```typescript
// ✅ 使用 2 空格缩进
function example() {
  if (condition) {
    doSomething();
  }
}

// ✅ 字符串使用单引号
const name = '张三';

// ✅ 模板字符串处理复杂字符串
const greeting = `Hello, ${name}!`;

// ✅ 对象/数组最后一个元素加逗号 (Trailing comma)
const config = {
  host: 'localhost',
  port: 3000,  // ← 逗号
};

// ✅ 一行最多 100 字符
const longString =
  '这是一段很长的文本，需要换行以提高可读性';

// ✅ 函数参数超过 3 个使用对象
// ❌ 不推荐
function createUser(name, email, password, role) {}

// ✅ 推荐
function createUser(params: {
  name: string;
  email: string;
  password: string;
  role: string;
}) {}
```

#### 1.3 TypeScript 类型规范

```typescript
// ✅ 避免使用 any
// ❌ 不推荐
function process(data: any) {}

// ✅ 推荐 - 使用 unknown 或具体类型
function process(data: unknown) {}
function processUser(data: User) {}

// ✅ 函数返回值明确标注
function add(a: number, b: number): number {
  return a + b;
}

// ✅ 接口定义清晰
interface Slide {
  id: string;
  title: string;
  content?: string;        // 可选属性
  readonly createdAt: Date; // 只读属性
}

// ✅ 使用联合类型代替枚举
type Status = 'pending' | 'processing' | 'completed' | 'failed';

// ✅ null 检查
function getLength(str: string | null): number {
  return str?.length ?? 0;
}
```

#### 1.4 React 组件规范

```typescript
// ✅ 组件名 PascalCase
function UserProfile() {}
function SlideEditor() {}

// ✅ Props 接口定义
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

function UserProfile({ userId, onUpdate }: UserProfileProps) {}

// ✅ Hooks 使用规范
function useSlideData(id: string) {
  const [data, setData] = useState<Slide | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // 清理函数
    const controller = new AbortController();
    fetchData(id, { signal: controller.signal });
    return () => controller.abort();
  }, [id]); // 依赖项完整

  return { data, loading };
}

// ✅ 事件处理函数命名
function handleClick() {}
function handleSubmit(event: FormEvent) {}
function handleInputChange(value: string) {}

// ❌ 禁止
function onClick() {}  // 组件内的 handler 不要用 on 前缀
```

### 2. CSS / SCSS 规范

#### 2.1 命名规范 (BEM 方法论)

```scss
// ✅ BEM 命名
// Block - 组件块
.slide-editor {}

// Element - 元素
.slide-editor__header {}
.slide-editor__content {}
.slide-editor__footer {}

// Modifier - 修饰符
.slide-editor--fullscreen {}
.slide-editor__button--primary {}
.slide-editor__button--disabled {}

// ❌ 禁止
.slideEditor {}         // 驼峰命名
.slide_editor {}        // 蛇形命名
.sd-ed-hd {}           // 缩写不清晰
```

#### 2.2 CSS 属性顺序 (腾讯 AlloyTeam 规范)

```scss
.element {
  // 1. 布局属性
  display: flex;
  visibility: visible;
  float: none;
  clear: both;
  overflow: hidden;
  
  // 2. 定位属性
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 100;
  
  // 3. 盒模型属性 (由外到内)
  margin: 10px;
  margin-top: 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 20px;
  width: 100%;
  height: auto;
  box-sizing: border-box;
  
  // 4. 字体排版
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
  text-align: center;
  
  // 5. 视觉效果
  color: #333;
  background-color: #f5f5f5;
  background-image: url(...);
  opacity: 1;
  
  // 6. 动画效果
  transition: all 0.3s ease;
  transform: translateX(0);
  animation: fadeIn 0.5s;
  
  // 7. 其他
  cursor: pointer;
  user-select: none;
}
```

#### 2.3 CSS 最佳实践

```scss
// ✅ 使用 CSS 变量
:root {
  --color-primary: #1890ff;
  --color-danger: #ff4d4f;
  --spacing-base: 8px;
}

.button-primary {
  background-color: var(--color-primary);
}

// ✅ 使用 flexbox/grid 布局
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

// ✅ 响应式断点
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}

// ❌ 禁止
.button { color: #1890ff; }  // 硬编码颜色
.element { width: 100px; height: 100px; }  // 魔数
```

---

## 🐍 后端代码规范 (Python)

### 1. 命名规范 (PEP 8 + 腾讯规范)

```python
# ✅ 模块名 - 小写下划线
# user_service.py, auth_controller.py

# ✅ 包名 - 小写无下划线
# services, models, utils

# ✅ 类名 - PascalCase
class UserService:
    pass

class SlideEditor:
    pass

# ✅ 函数/变量 - 小写下划线
def get_user_by_id(user_id: str) -> User:
    user_name = "张三"
    return user

# ✅ 常量 - 全大写下划线
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# ✅ 私有属性/方法 - 单下划线前缀
class UserService:
    def _internal_method(self):  # 保护方法
        pass
    
    def __private_method(self):  # 私有方法 (避免使用)
        pass

# ✅ 魔术方法 - 双下划线前后缀
class User:
    def __init__(self):
        pass
    
    def __str__(self) -> str:
        return f"User({self.id})"

# ❌ 禁止
class userService: pass      # 驼峰命名类
def GetUser(): pass          # 驼峰命名函数
userName = ""                # 驼峰命名变量
```

### 2. 代码格式

```python
# ✅ 每行最多 88 字符 (Black 默认)
# 超出时合理换行
result = some_long_function_name(
    param1=value1,
    param2=value2,
    param3=value3,
)

# ✅ 函数/类之间空两行
class UserService:
    pass


class SlideService:
    pass


# ✅ 类内方法之间空一行
class UserService:
    def method_one(self):
        pass
    
    def method_two(self):
        pass

# ✅ import 分组排序
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
from fastapi import FastAPI
from sqlalchemy import Column

# 3. 本地模块
from .models import User
from .utils import hash_password
```

### 3. FastAPI 规范

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# ✅ Request/Response Schema 明确定义
class UserCreateRequest(BaseModel):
    """用户创建请求"""
    email: str
    password: str
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure123",
                "name": "张三"
            }
        }


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ✅ 路由处理函数规范
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账户，返回用户信息"
)
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    创建新用户
    
    - **email**: 用户邮箱，必须唯一
    - **password**: 密码，至少8位
    - **name**: 用户显示名称
    """
    try:
        user = await service.create_user(request)
        return UserResponse.model_validate(user)
    except EmailExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邮箱已被注册"
        )
```

### 4. SQLAlchemy ORM 规范

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    # ✅ 主键使用 UUID
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # ✅ 字段注释清晰
    email = Column(String(255), unique=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    name = Column(String(100), nullable=False, comment="用户名")
    
    # ✅ 时间戳字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # ✅ 关系定义
    presentations = relationship("Presentation", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
```

### 5. 异常处理规范

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# ✅ 自定义异常层次
class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(AppError):
    """参数验证错误"""
    pass


class NotFoundError(AppError):
    """资源不存在"""
    pass


class BusinessError(AppError):
    """业务逻辑错误"""
    pass


# ✅ 异常处理最佳实践
def process_data(data: dict) -> Result:
    try:
        validated = validate_data(data)
        return process_validated(validated)
    except ValidationError as e:
        # 已知异常 - 记录警告，返回友好提示
        logger.warning(f"Validation failed: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        # 未知异常 - 记录错误详情，返回模糊提示
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
```

---

## 🔒 安全编码规范 (基于腾讯 secguide)

### 1. Python 安全

```python
# ✅ SQL 注入防护 - 使用参数化查询
# ❌ 危险
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ 安全
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SQLAlchemy 会自动处理参数化
User.query.filter(User.id == user_id).first()


# ✅ 命令注入防护
import subprocess

# ❌ 危险
os.system(f"ping {host}")
subprocess.call(f"convert {input_file} {output_file}", shell=True)

# ✅ 安全 - 使用列表传参，禁用 shell
subprocess.run(["ping", host], capture_output=True)
subprocess.run(["convert", input_file, output_file], capture_output=True)


# ✅ 路径遍历防护
import os
from pathlib import Path

# ❌ 危险
file_path = f"/uploads/{user_input}"

# ✅ 安全
base_path = Path("/uploads").resolve()
file_path = (base_path / user_input).resolve()
if not str(file_path).startswith(str(base_path)):
    raise ValueError("非法路径")


# ✅ 反序列化安全
import json
import pickle

# ✅ 安全 - 使用 json
json.loads(user_input)

# ❌ 危险 - pickle 可执行任意代码
data = pickle.loads(untrusted_data)


# ✅ 敏感数据处理
import bcrypt
from cryptography.fernet import Fernet

# 密码哈希
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
is_valid = bcrypt.checkpw(password.encode(), password_hash)

# 加密敏感数据
key = os.environ.get("ENCRYPTION_KEY")
cipher = Fernet(key)
encrypted = cipher.encrypt(sensitive_data.encode())
```

### 2. JavaScript/TypeScript 安全

```typescript
// ✅ XSS 防护 - 不直接插入 HTML
// ❌ 危险
element.innerHTML = userInput;

// ✅ 安全
element.textContent = userInput;

// 或使用 DOMPurify 清理
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);


// ✅ URL 验证
// ❌ 危险
window.location.href = redirectUrl;

// ✅ 安全
const allowedHosts = ['example.com', 'api.example.com'];
const url = new URL(redirectUrl);
if (allowedHosts.includes(url.hostname)) {
  window.location.href = redirectUrl;
}


// ✅ eval 禁用
// ❌ 绝对禁止
eval(userCode);
new Function(userCode)();
setTimeout(userCode, 1000);

// ✅ 使用 JSON.parse 替代
const data = JSON.parse(jsonString);
```

### 3. 认证与授权安全

```python
# ✅ JWT 安全
import jwt
from datetime import datetime, timedelta

# 密钥从环境变量读取
JWT_SECRET = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token 已过期")
    except jwt.InvalidTokenError:
        raise AuthenticationError("无效的 Token")


# ✅ 密码策略
import re
from zxcvbn import zxcvbn

def validate_password(password: str) -> bool:
    """密码强度验证"""
    # 长度至少 8 位
    if len(password) < 8:
        return False
    
    # 使用 zxcvbn 评估强度
    result = zxcvbn(password)
    return result["score"] >= 3  # 0-4 分，要求至少 3 分
```

---

## 📝 注释与文档规范

### 1. 文件头注释

```python
"""
模块名称: user_service.py
功能描述: 用户相关业务逻辑处理
作者: Backend Agent
创建时间: 2026-02-13
修改历史:
    2026-02-13: 创建文件，实现基础 CRUD
"""

# 或者 TypeScript
/**
 * @fileoverview 用户服务模块
 * @author Frontend Agent
 * @date 2026-02-13
 */
```

### 2. 函数/方法注释

```python
def get_user_by_email(
    email: str,
    include_deleted: bool = False
) -> Optional[User]:
    """
    根据邮箱获取用户信息
    
    Args:
        email: 用户邮箱地址
        include_deleted: 是否包含已删除用户，默认 False
    
    Returns:
        User 对象，未找到时返回 None
    
    Raises:
        DatabaseError: 数据库查询失败
    
    Example:
        >>> user = get_user_by_email("user@example.com")
        >>> if user:
        ...     print(user.name)
    """
```

### 3. 代码内注释

```python
# ✅ 解释 "为什么" 而不是 "是什么"
# 用户可能输入带空格的邮箱，需要清理
email = email.strip().lower()

# ✅ 复杂逻辑的分步说明
# Step 1: 验证 JWT Token
decoded = jwt.decode(token, secret, algorithms=["HS256"])

# Step 2: 检查用户是否存在
user = await get_user(decoded["user_id"])
if not user:
    raise AuthenticationError("用户不存在")

# Step 3: 验证用户状态
if user.is_disabled:
    raise AuthenticationError("账户已禁用")

# ❌ 禁止 - 显而易见的注释
# 将 i 加 1
i += 1
```

---

## 🔧 工具配置

### 1. 前端 ESLint 配置

```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "next/typescript",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "no-console": ["warn", { "allow": ["error"] }],
    "prefer-const": "error"
  }
}
```

### 2. 后端 Black 配置

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

### 3. Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
  
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
```

---

## ✅ 代码审查检查清单

### 提交前自检

- [ ] 代码通过所有 lint 检查
- [ ] 类型检查无错误
- [ ] 单元测试全部通过
- [ ] 新增代码覆盖率 ≥ 80%
- [ ] 安全扫描无高危漏洞
- [ ] 敏感信息未硬编码
- [ ] 注释清晰完整
- [ ] 文档已更新

### 审查重点

| 检查项 | 优先级 | 检查方法 |
|--------|--------|----------|
| 安全漏洞 | 🔴 P0 | bandit, ESLint security |
| 代码风格 | 🟡 P1 | Black, ESLint |
| 测试覆盖 | 🔴 P0 | pytest --cov |
| 类型安全 | 🟡 P1 | mypy, TypeScript |
| 性能问题 | 🟢 P2 | 代码审查 |
| 可读性 | 🟡 P1 | 人工审查 |

---

## 📚 参考资源

1. **腾讯 secguide**: https://github.com/Tencent/secguide
2. **AlloyTeam Code Guide**: https://alloyteam.github.io/CodeGuide/
3. **PEP 8**: https://peps.python.org/pep-0008/
4. **Google TypeScript Style**: https://google.github.io/styleguide/tsguide.html
5. **FastAPI Best Practices**: https://github.com/zhanymkanov/fastapi-best-practices

---

**生效日期**: 2026-02-13  
**规范版本**: 1.0.0  
**审核周期**: 每季度审查更新

---

*"写出诗一样的代码" - 腾讯 AlloyTeam*
