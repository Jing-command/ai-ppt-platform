# API Contract v1.3

> AI PPT Platform - 完整 API 契约文档  
> 版本: 1.3  
> 更新日期: 2026-02-15  
> 状态: 已实现

## 通用规范

### 基础信息
- **Base URL**: `/api/v1`
- **协议**: HTTPS (生产环境) / HTTP (开发环境)
- **认证方式**: Bearer Token
- **请求格式**: JSON (`Content-Type: application/json`)
- **响应格式**: JSON
- **命名规范**: camelCase
- **字符编码**: UTF-8

### 认证头
所有受保护的端点需要在请求头中包含认证信息：
```
Authorization: Bearer {accessToken}
```

### 通用响应结构

#### 成功响应 (200-299)
直接返回数据对象或数组。

#### 分页响应
```typescript
interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
```

#### 错误响应
```typescript
interface ErrorResponse {
  code: string;        // 错误代码
  message: string;     // 错误描述
  details?: object;    // 详细错误信息
}
```

---

## 类型定义

### 通用类型

#### PaginationParams
```typescript
interface PaginationParams {
  page?: number;       // 默认: 1, 最小: 1
  pageSize?: number;   // 默认: 20, 范围: 1-100
}
```

#### PaginationMeta
```typescript
interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}
```

---

### Auth 模块

#### User
```typescript
interface User {
  id: string;          // UUID
  email: string;       // format: email
  name: string;        // 用户名
  avatar?: string;     // 头像URL（可选）
  createdAt: string;   // ISO 8601 datetime
}
```

#### UpdateUserRequest
```typescript
interface UpdateUserRequest {
  name?: string;       // 用户名，minLength: 1, maxLength: 100
  avatar_url?: string; // 头像URL
}
```

#### AvatarUploadResponse
```typescript
interface AvatarUploadResponse {
  avatarUrl: string;   // 上传后的头像URL
}
```

#### LoginRequest
```typescript
interface LoginRequest {
  email: string;       // format: email
  password: string;    // minLength: 6
}
```

#### LoginResponse
```typescript
interface LoginResponse {
  accessToken: string;
  tokenType: "bearer";
  user: User;
}
```

#### RegisterRequest
```typescript
interface RegisterRequest {
  email: string;       // format: email
  password: string;    // minLength: 6
  name: string;        // minLength: 1, maxLength: 100
}
```

#### RegisterResponse
```typescript
interface RegisterResponse extends LoginResponse {}
```

#### RefreshRequest
```typescript
interface RefreshRequest {
  refreshToken: string;
}
```

#### RefreshResponse
```typescript
interface RefreshResponse {
  accessToken: string;
  tokenType: "bearer";
}
```

---

### Chat 模块

#### MessageRole
```typescript
type MessageRole = "user" | "assistant" | "system";
```

#### ChatMessage
```typescript
interface ChatMessage {
  role: MessageRole;     // 消息角色
  content: string;       // 消息内容
}
```

#### ChatContext
```typescript
interface ChatContext {
  presentationId?: string;   // 当前演示文稿 ID
  slideId?: string;          // 当前幻灯片 ID
  currentPrompt?: string;    // 用户当前正在编辑的提示词
  metadata?: Record<string, any>;  // 额外的元数据信息
}
```

#### ChatRequest
```typescript
interface ChatRequest {
  messages: ChatMessage[];   // 聊天消息列表，minLength: 1
  context?: ChatContext;     // 可选的上下文信息
  stream?: boolean;          // 是否使用流式响应，默认: true
}
```

#### ChatResponseChunk
```typescript
interface ChatResponseChunk {
  content: string;               // 响应内容片段
  isFinished: boolean;           // 是否响应结束
  hasOptimizedPrompt: boolean;   // 是否包含优化后的提示词
  optimizedPrompt?: string;      // 优化后的提示词
}
```

#### ChatResponse
```typescript
interface ChatResponse {
  message: ChatMessage;          // AI 响应消息
  hasOptimizedPrompt: boolean;   // 是否包含优化后的提示词
  optimizedPrompt?: string;      // 优化后的提示词
}
```

#### IntentType
```typescript
type IntentType = "clarification" | "prompt_optimization" | "suggestion" | "general";
```

#### IntentAnalysis
```typescript
interface IntentAnalysis {
  intentType: IntentType;        // 意图类型
  confidence: number;            // 置信度 (0.0 - 1.0)
  missingInfo?: string[];        // 缺失的信息列表
  suggestedQuestions?: string[]; // 建议的问题列表
}
```

---

### Connectors 模块

#### ConnectorBase
```typescript
interface ConnectorBase {
  name: string;                    // minLength: 1, maxLength: 100
  type: string;                    // mysql, postgresql, mongodb, csv, api
  description?: string;            // maxLength: 500
}
```

#### ConnectorCreate
```typescript
interface ConnectorCreate extends ConnectorBase {
  config: Record<string, any>;     // 连接配置参数
}
```

#### ConnectorUpdate
```typescript
interface ConnectorUpdate {
  name?: string;                   // minLength: 1, maxLength: 100
  description?: string;            // maxLength: 500
  config?: Record<string, any>;
  isActive?: boolean;
}
```

#### ConnectorResponse
```typescript
interface ConnectorResponse extends ConnectorBase {
  id: string;                      // UUID
  userId: string;                  // UUID
  config: Record<string, any>;     // 脱敏后的配置
  isActive: boolean;
  lastTestedAt?: string;           // ISO 8601 datetime
  lastTestStatus?: "success" | "failed";
  createdAt: string;               // ISO 8601 datetime
  updatedAt: string;               // ISO 8601 datetime
}
```

#### ConnectorDetailResponse
```typescript
interface ConnectorDetailResponse extends ConnectorResponse {}
```

#### ConnectorTestRequest
```typescript
interface ConnectorTestRequest {
  config?: Record<string, any>;    // 临时配置用于测试
}
```

#### ConnectorTestResponse
```typescript
interface ConnectorTestResponse {
  success: boolean;
  message: string;
  latencyMs?: number;              // 连接延迟毫秒
  serverVersion?: string;
  errorDetails?: string;
}
```

#### DatabaseColumn
```typescript
interface DatabaseColumn {
  name: string;
  type: string;
  isNullable: boolean;
  isPrimaryKey: boolean;
  defaultValue?: string;
  comment?: string;
}
```

#### DatabaseTable
```typescript
interface DatabaseTable {
  name: string;
  schema?: string;
  comment?: string;
  columns: DatabaseColumn[];
  rowCount?: number;
}
```

#### ConnectorSchemaResponse
```typescript
interface ConnectorSchemaResponse {
  connectorId: string;             // UUID
  tables: DatabaseTable[];
  views?: DatabaseTable[];
}
```

#### ConnectorQueryRequest
```typescript
interface ConnectorQueryRequest {
  query: string;                   // minLength: 1, SQL 查询
  params?: Record<string, any>;    // 查询参数
  limit?: number;                  // 默认: 100, 范围: 1-10000
}
```

#### QueryResultColumn
```typescript
interface QueryResultColumn {
  name: string;
  type: string;
}
```

#### ConnectorQueryResponse
```typescript
interface ConnectorQueryResponse {
  success: boolean;
  columns: QueryResultColumn[];
  rows: Record<string, any>[];
  rowCount: number;
  executionTimeMs: number;
  query: string;
}
```

---

### Outlines 模块

#### OutlineSection (页面大纲)
```typescript
interface OutlineSection {
  id: string;                      // 页面 ID
  pageNumber: number;              // 页码 (1, 2, 3...)
  title: string;                   // 页面标题，minLength: 1, maxLength: 200
  content?: string;                // 页面内容描述，maxLength: 1000
  pageType?: "title" | "content" | "section" | "chart" | "conclusion";  // 页面类型
  layout?: string;                 // 布局模板
  notes?: string;                  // 演讲备注
  imagePrompt?: string;            // 插图提示词（AI生成或用户编辑）
}

#### OutlineBackground
PPT背景设置

```typescript
interface OutlineBackground {
  type: "ai" | "upload" | "solid";  // 背景类型：AI生成/上传图片/纯色
  prompt?: string;                   // AI生成背景时的提示词
  url?: string;                      // 上传图片的URL
  color?: string;                    // 纯色背景的颜色值 (hex)
  opacity?: number;                  // 背景透明度 (0-1)，默认1
  blur?: number;                     // 背景模糊度 (0-20px)，默认0
}
```
```

#### OutlineBase
```typescript
interface OutlineBase {
  title: string;                   // minLength: 1, maxLength: 200
  description?: string;            // maxLength: 1000
}
```

#### OutlineCreate
```typescript
interface OutlineCreate extends OutlineBase {
  pages?: OutlineSection[];
  background?: OutlineBackground;
}
```

#### OutlineUpdate
```typescript
interface OutlineUpdate {
  title?: string;                  // minLength: 1, maxLength: 200
  description?: string;            // maxLength: 1000
  pages?: OutlineSection[];
  background?: OutlineBackground;
}
```

#### OutlineResponse
```typescript
interface OutlineResponse extends OutlineBase {
  id: string;                      // UUID
  userId: string;                  // UUID
  pages: OutlineSection[];         // 页面列表（按 pageNumber 排序）
  background?: OutlineBackground;  // PPT背景设置
  totalSlides: number;             // 总页数
  status: "draft" | "generating" | "completed" | "archived";
  aiPrompt?: string;
  aiParameters?: Record<string, any>;
  createdAt: string;               // ISO 8601 datetime
  updatedAt: string;               // ISO 8601 datetime
  generatedAt?: string;            // ISO 8601 datetime
}
```
```

#### OutlineDetailResponse
```typescript
interface OutlineDetailResponse extends OutlineResponse {}
```

#### OutlineGenerateRequest
```typescript
interface OutlineGenerateRequest {
  prompt: string;                  // minLength: 10, maxLength: 2000
  numSlides?: number;              // 范围: 3-50, 默认: 15 - PPT总页数
  language?: "zh" | "en";          // 默认: "zh"
  style?: "business" | "education" | "creative" | "technical";  // 默认: "business"
  contextData?: Record<string, any>;
  connectorId?: string;            // UUID
}
```

#### OutlineGenerateResponse
```typescript
interface OutlineGenerateResponse {
  taskId: string;                  // UUID
  status: "pending" | "processing" | "completed" | "failed";
  estimatedTime: number;           // 预估秒数
  message: string;
}
```

#### OutlineToPresentationRequest
```typescript
interface OutlineToPresentationRequest {
  title?: string;                  // 自定义标题
  templateId?: string;
  theme?: string;
  slideLayout?: "auto" | "detailed" | "minimal";  // 默认: "auto"
  generateContent?: boolean;       // 默认: true
  provider?: string;               // AI 提供商
}
```

#### OutlineToPresentationResponse
```typescript
interface OutlineToPresentationResponse {
  presentationId: string;          // UUID
  taskId: string;                  // UUID
  status: string;
  message: string;
  estimatedTime: number;
}
```

---

### Presentations 模块

#### SlideContent
```typescript
interface SlideContent {
  title?: string;
  subtitle?: string;
  description?: string;
  text?: string;
  secondColumn?: string;
  bullets?: string[];
  imageUrl?: string;
  chartData?: Record<string, any>;
  stats?: Record<string, any>[];   // data layout
  events?: Record<string, any>[];  // timeline layout
  steps?: string[];                // process layout
  items?: Record<string, any>[];   // grid/comparison layout
  left?: Record<string, any>;      // two-column layout
  right?: Record<string, any>;     // two-column layout
  quote?: string;                  // quote layout
  author?: string;                 // quote layout
}
```

#### SlideLayout
```typescript
interface SlideLayout {
  type: "title" | "content" | "split" | "image" | "chart" | "timeline" | "data" | "quote";
  background?: string;
  theme?: string;
}
```

#### SlideStyle
```typescript
interface SlideStyle {
  fontFamily?: string;
  fontSize?: number;
  color?: string;
  alignment?: string;
}
```

#### Slide
```typescript
interface Slide {
  id?: string;
  type: string;                    // 默认: "content"
  content: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  orderIndex: number;              // 默认: 0
}
```

#### PresentationBase
```typescript
interface PresentationBase {
  title: string;                   // minLength: 1, maxLength: 255
}
```

#### PresentationCreate
```typescript
interface PresentationCreate extends PresentationBase {
  description?: string;            // maxLength: 1000
  templateId?: string;
  outlineId?: string;              // UUID
  slides?: Slide[];
}
```

#### PresentationUpdate
```typescript
interface PresentationUpdate {
  title?: string;                  // minLength: 1, maxLength: 255
  description?: string;            // maxLength: 1000
  slides?: Slide[];
  status?: "draft" | "published" | "archived";
  templateId?: string;
}
```

#### PresentationResponse
```typescript
interface PresentationResponse extends PresentationBase {
  id: string;                      // UUID
  ownerId: string;                 // UUID - 演示文稿所有者
  outlineId?: string;              // UUID
  templateId?: string;
  slideCount: number;
  status: "draft" | "published" | "archived";
  version: number;                 // 默认: 1
  createdAt: string;               // ISO 8601 datetime
  updatedAt: string;               // ISO 8601 datetime
}
```

#### PresentationDetailResponse
```typescript
interface PresentationDetailResponse extends PresentationBase {
  id: string;                      // UUID
  ownerId: string;                 // UUID - 演示文稿所有者
  outlineId?: string;              // UUID
  templateId?: string;
  description?: string;
  slides: Slide[];
  slideCount: number;
  status: "draft" | "published" | "archived";
  version: number;
  aiPrompt?: string;
  aiParameters?: Record<string, any>;
  createdAt: string;               // ISO 8601 datetime
  updatedAt: string;               // ISO 8601 datetime
}
```

#### SlideCreate
```typescript
interface SlideCreate {
  type?: string;                   // 默认: "content"
  content: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  position?: number;               // 插入位置，null 表示末尾
}
```

#### SlideUpdate
```typescript
interface SlideUpdate {
  type?: string;
  content?: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  orderIndex?: number;             // 最小: 0
}
```

#### SlideResponse
```typescript
interface SlideResponse extends Slide {
  createdAt?: string;              // ISO 8601 datetime
  updatedAt?: string;              // ISO 8601 datetime
}
```

#### GenerateRequest
```typescript
interface GenerateRequest {
  prompt: string;                  // minLength: 10, maxLength: 2000
  templateId?: string;
  numSlides?: number;              // 范围: 1-50, 默认: 10
  language?: "zh" | "en";          // 默认: "zh"
  style?: "business" | "education" | "creative" | "minimal";  // 默认: "business"
  provider?: string;
}
```

#### GenerateResponse
```typescript
interface GenerateResponse {
  taskId: string;                  // UUID
  status: string;
  estimatedTime: number;           // 预估秒数
  message: string;
}
```

#### GenerateStatusResponse
```typescript
interface GenerateStatusResponse {
  taskId: string;                  // UUID
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  progress: number;                // 0-100
  result?: Record<string, any>;
  errorMessage?: string;
  createdAt: string;               // ISO 8601 datetime
  updatedAt: string;               // ISO 8601 datetime
  completedAt?: string;            // ISO 8601 datetime
}
```

---

### Slides 模块

#### UndoRedoResponse
```typescript
interface UndoRedoResponse {
  success: boolean;
  description: string;
  state?: Record<string, any>;
  slideId?: string;
}
```

---

### Exports 模块

#### ExportRequest
```typescript
interface ExportRequest {
  format: "pptx" | "pdf" | "png" | "jpg";
  quality?: "standard" | "high";   // 默认: "standard"
  slideRange?: string;             // 如 "1-5" 或 "all"
  includeNotes?: boolean;          // 默认: false
}
```

#### ExportResponse
```typescript
interface ExportResponse {
  taskId: string;                  // UUID
  status: "pending" | "processing" | "completed" | "failed";
  downloadUrl?: string;
  fileSize?: number;               // 字节
  expiresAt?: string;              // ISO 8601 datetime
  createdAt: string;               // ISO 8601 datetime
}
```

#### ExportStatusResponse
```typescript
interface ExportStatusResponse {
  taskId: string;                  // UUID
  presentationId: string;          // UUID
  format: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;                // 0-100
  filePath?: string;
  fileSize?: number;               // 字节
  errorMessage?: string;
  downloadUrl?: string;
  expiresAt?: string;              // ISO 8601 datetime
  createdAt: string;               // ISO 8601 datetime
  completedAt?: string;            // ISO 8601 datetime
}
```

---

## 端点规范

### Chat 模块

#### POST /chat
**描述**: 发送聊天消息

**请求头**:
```
Authorization: Bearer {accessToken}  // 可选
Content-Type: application/json
```

**请求**:
```typescript
ChatRequest
```

**成功响应 (200)**:
- 流式响应: SSE (Server-Sent Events) 格式
- 非流式响应: `ChatResponse`

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `500` INTERNAL_ERROR - 服务器错误

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "帮我生成一个销售报告 PPT"}
    ],
    "context": {
      "presentationId": "xxx",
      "currentPrompt": "销售报告"
    },
    "stream": true
  }'
```

**响应示例 (SSE 格式)**:
```
data: {"content": "根据", "isFinished": false, "hasOptimizedPrompt": false}

data: {"content": "您的描述", "isFinished": false, "hasOptimizedPrompt": false}

data: {"content": "...", "isFinished": true, "hasOptimizedPrompt": true, "optimizedPrompt": "主题：销售报告\n目标受众：领导"}
```

**响应示例 (非流式)**:
```json
{
  "message": {
    "role": "assistant",
    "content": "根据您的描述，我已经为您优化了提示词..."
  },
  "hasOptimizedPrompt": true,
  "optimizedPrompt": "主题：销售报告\n目标受众：领导\n演示目的：工作汇报\n设计风格：商务专业"
}
```

---

#### POST /chat/analyze
**描述**: 分析用户意图

**请求头**:
```
Authorization: Bearer {accessToken}  // 可选
Content-Type: application/json
```

**请求**:
```typescript
ChatRequest
```

**成功响应 (200)**:
```typescript
IntentAnalysis
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `500` INTERNAL_ERROR - 服务器错误

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "帮我做一个PPT"}
    ]
  }'
```

**响应示例**:
```json
{
  "intentType": "clarification",
  "confidence": 0.85,
  "missingInfo": ["主题", "受众", "目的", "风格"],
  "suggestedQuestions": [
    "您想制作什么主题的 PPT？",
    "这个 PPT 的目标受众是谁？（如：客户、领导、同事等）",
    "您希望通过这个 PPT 达到什么目的？（如：汇报、销售、培训等）"
  ]
}
```

---

### Auth 模块

#### POST /auth/register
**描述**: 用户注册

**请求**:
```typescript
RegisterRequest
```

**成功响应 (201)**:
```typescript
RegisterResponse
```

**错误响应**:
- `400` EMAIL_EXISTS - 邮箱已被注册
- `400` USERNAME_EXISTS - 用户名已被使用
- `400` INVALID_REQUEST - 参数错误
- `422` VALIDATION_ERROR - 验证失败

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "123456",
    "name": "Test User"
  }'
```

**响应示例**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "name": "Test User",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

---

#### POST /auth/login
**描述**: 用户登录

**请求**:
```typescript
LoginRequest
```

**成功响应 (200)**:
```typescript
LoginResponse
```

**错误响应**:
- `401` INVALID_CREDENTIALS - 邮箱或密码错误
- `403` USER_INACTIVE - 用户账户已被禁用
- `422` VALIDATION_ERROR - 验证失败

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "123456"
  }'
```

**响应示例**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "name": "Test User",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

---

#### POST /auth/refresh
**描述**: 刷新访问令牌

**请求**:
```typescript
RefreshRequest
```

**成功响应 (200)**:
```typescript
RefreshResponse
```

**错误响应**:
- `401` INVALID_TOKEN - 无效的刷新令牌
- `401` TOKEN_EXPIRED - 刷新令牌已过期
- `401` USER_NOT_FOUND - 用户不存在
- `403` USER_INACTIVE - 用户账户已被禁用

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**响应示例**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer"
}
```

---

#### GET /auth/me
**描述**: 获取当前用户信息

**请求头**:
```
Authorization: Bearer {accessToken}
```

**成功响应 (200)**:
```typescript
UserResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `403` USER_INACTIVE - 用户账户已被禁用

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "name": "Test User",
  "avatar": "https://cdn.example.com/avatars/xxx.jpg",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

#### PUT /auth/me
**描述**: 更新当前用户信息

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
UpdateUserRequest
```

**成功响应 (200)**:
```typescript
User
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新用户名"
  }'
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "name": "新用户名",
  "avatar": "https://cdn.example.com/avatars/xxx.jpg",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

#### POST /auth/me/avatar
**描述**: 上传用户头像

**请求头**:
```
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data
```

**请求体**:
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 头像图片文件，支持 jpg/png/gif/webp，最大 2MB |

**成功响应 (200)**:
```typescript
AvatarUploadResponse
```

**错误响应**:
- `400` INVALID_FILE_TYPE - 不支持的文件类型
- `400` FILE_TOO_LARGE - 文件大小超过限制
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/me/avatar \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@/path/to/avatar.jpg"
```

**响应示例**:
```json
{
  "avatarUrl": "https://cdn.example.com/avatars/550e8400-e29b-41d4-a716-446655440000.jpg"
}
```

---

### Connectors 模块

#### GET /connectors
**描述**: 获取连接器列表

**请求头**:
```
Authorization: Bearer {accessToken}
```

**查询参数**:
```typescript
{
  page?: number;        // 默认: 1
  pageSize?: number;    // 默认: 20
  connectorType?: string;  // 可选过滤
}
```

**成功响应 (200)**:
```typescript
PaginatedResponse<ConnectorResponse>
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/connectors?page=1&pageSize=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "销售数据库",
      "type": "mysql",
      "description": "销售数据MySQL数据库",
      "userId": "550e8400-e29b-41d4-a716-446655440001",
      "config": {
        "host": "localhost",
        "port": 3306,
        "database": "sales"
      },
      "isActive": true,
      "lastTestedAt": "2024-01-01T00:00:00Z",
      "lastTestStatus": "success",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

---

#### POST /connectors
**描述**: 创建连接器

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
ConnectorCreate
```

**成功响应 (201)**:
```typescript
ConnectorResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `409` NAME_EXISTS - 名称已存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/connectors \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "销售数据库",
    "type": "mysql",
    "description": "连接销售数据MySQL数据库",
    "config": {
      "host": "localhost",
      "port": 3306,
      "database": "sales",
      "username": "readonly",
      "password": "secret"
    }
  }'
```

---

#### GET /connectors/{id}
**描述**: 获取连接器详情

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**成功响应 (200)**:
```typescript
ConnectorDetailResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### PUT /connectors/{id}
**描述**: 更新连接器

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**请求**:
```typescript
ConnectorUpdate
```

**成功响应 (200)**:
```typescript
ConnectorResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在

**示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "销售数据库（新）",
    "description": "更新的描述",
    "isActive": true
  }'
```

---

#### DELETE /connectors/{id}
**描述**: 删除连接器

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**成功响应 (204)**: 无内容

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在

**示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /connectors/{id}/test
**描述**: 测试连接

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**请求**:
```typescript
ConnectorTestRequest  // config 可选，用于测试临时配置
```

**成功响应 (200)**:
```typescript
ConnectorTestResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000/test \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "host": "localhost",
      "port": 3306,
      "database": "sales"
    }
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "连接成功",
  "latencyMs": 45,
  "serverVersion": "8.0.33"
}
```

---

#### GET /connectors/{id}/schema
**描述**: 获取数据源结构

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**查询参数**:
- `refresh` (boolean, 可选) - 是否刷新缓存

**成功响应 (200)**:
```typescript
ConnectorSchemaResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在
- `502` CONNECTION_FAILED - 连接失败

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000/schema?refresh=false" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "connectorId": "550e8400-e29b-41d4-a716-446655440000",
  "tables": [
    {
      "name": "sales",
      "schema": "public",
      "comment": "销售记录表",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "isNullable": false,
          "isPrimaryKey": true,
          "defaultValue": null,
          "comment": "主键"
        }
      ],
      "rowCount": 10000
    }
  ],
  "views": []
}
```

---

#### POST /connectors/{id}/query
**描述**: 执行查询

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 连接器 ID

**请求**:
```typescript
ConnectorQueryRequest
```

**成功响应 (200)**:
```typescript
ConnectorQueryResponse
```

**错误响应**:
- `400` INVALID_QUERY - 查询语法错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 连接器不存在
- `502` QUERY_FAILED - 查询执行失败

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/connectors/550e8400-e29b-41d4-a716-446655440000/query \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM sales WHERE date >= :start_date LIMIT 100",
    "params": {"start_date": "2024-01-01"},
    "limit": 100
  }'
```

**响应示例**:
```json
{
  "success": true,
  "columns": [
    {"name": "id", "type": "INTEGER"},
    {"name": "amount", "type": "DECIMAL"}
  ],
  "rows": [
    {"id": 1, "amount": 100.50}
  ],
  "rowCount": 1,
  "executionTimeMs": 125,
  "query": "SELECT * FROM sales WHERE date >= :start_date LIMIT 100"
}
```

---

### Outlines 模块

#### GET /outlines
**描述**: 获取大纲列表

**请求头**:
```
Authorization: Bearer {accessToken}
```

**查询参数**:
```typescript
{
  page?: number;      // 默认: 1
  pageSize?: number;  // 默认: 20
  status?: string;    // 可选过滤: draft, generating, completed, archived
}
```

**成功响应 (200)**:
```typescript
PaginatedResponse<OutlineResponse>
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/outlines?page=1&pageSize=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /outlines
**描述**: 手动创建大纲

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
OutlineCreate
```

**成功响应 (201)**:
```typescript
OutlineResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/outlines \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "人工智能发展概述",
    "description": "介绍AI发展历程、现状和未来趋势",
    "sections": [
      {
        "title": "第一章：AI 的起源",
        "description": "早期人工智能发展历程",
        "estimatedSlides": 3,
        "orderIndex": 0
      }
    ]
  }'
```

---

#### POST /outlines/generate
**描述**: AI 生成大纲

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
OutlineGenerateRequest
```

**成功响应 (202)**:
```typescript
OutlineGenerateResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 提示词过短或参数错误
- `401` UNAUTHORIZED - 未认证
- `429` RATE_LIMITED - 请求过于频繁

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/outlines/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "制作一个关于人工智能在医疗领域应用的PPT",
    "numSections": 6,
    "slidesPerSection": 2,
    "language": "zh",
    "style": "business"
  }'
```

**响应示例**:
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "estimatedTime": 30,
  "message": "大纲生成任务已提交"
}
```

---

#### GET /outlines/{id}
**描述**: 获取大纲详情

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 大纲 ID

**成功响应 (200)**:
```typescript
OutlineDetailResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 大纲不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/outlines/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### PUT /outlines/{id}
**描述**: 更新大纲

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 大纲 ID

**请求**:
```typescript
OutlineUpdate
```

**成功响应 (200)**:
```typescript
OutlineResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 大纲不存在

**示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/outlines/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新的标题",
    "sections": [
      {
        "id": "section-1",
        "title": "第一章",
        "estimatedSlides": 4,
        "orderIndex": 0
      }
    ]
  }'
```

---

#### DELETE /outlines/{id}
**描述**: 删除大纲

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 大纲 ID

**成功响应 (204)**: 无内容

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 大纲不存在

**示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/outlines/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /outlines/{id}/presentations
**描述**: 基于大纲创建 PPT

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 大纲 ID

**请求**:
```typescript
OutlineToPresentationRequest
```

**成功响应 (202)**:
```typescript
OutlineToPresentationResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 大纲不存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/outlines/550e8400-e29b-41d4-a716-446655440000/presentations \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "templateId": "business-modern",
    "theme": "blue",
    "slideLayout": "auto",
    "generateContent": true
  }'
```

**响应示例**:
```json
{
  "presentationId": "550e8400-e29b-41d4-a716-446655440001",
  "taskId": "550e8400-e29b-41d4-a716-446655440002",
  "status": "pending",
  "message": "PPT 生成任务已提交",
  "estimatedTime": 60
}
```

---

### Presentations 模块

#### GET /presentations
**描述**: 获取 PPT 列表

**请求头**:
```
Authorization: Bearer {accessToken}
```

**查询参数**:
```typescript
{
  page?: number;      // 默认: 1
  pageSize?: number;  // 默认: 20
  status?: string;    // 可选过滤: draft, published, archived
}
```

**成功响应 (200)**:
```typescript
PaginatedResponse<PresentationResponse>
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/presentations?page=1&pageSize=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /presentations
**描述**: 创建 PPT

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
PresentationCreate
```

**成功响应 (201)**:
```typescript
PresentationDetailResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/presentations \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI 产品介绍",
    "description": "这是一个关于 AI 产品的介绍 PPT",
    "templateId": "business-modern",
    "slides": []
  }'
```

---

#### POST /presentations/generate
**描述**: AI 直接生成 PPT

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
GenerateRequest
```

**成功响应 (202)**:
```typescript
GenerateResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 提示词过短或参数错误
- `401` UNAUTHORIZED - 未认证
- `429` RATE_LIMITED - 请求过于频繁

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/presentations/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "制作一个关于人工智能发展历程的 PPT",
    "numSlides": 8,
    "language": "zh",
    "style": "business"
  }'
```

---

#### GET /presentations/{id}
**描述**: 获取 PPT 详情

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - PPT ID

**成功响应 (200)**:
```typescript
PresentationDetailResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "AI 产品介绍",
  "ownerId": "550e8400-e29b-41d4-a716-446655440001",
  "outlineId": null,
  "templateId": "business-modern",
  "description": "这是一个关于 AI 产品的介绍 PPT",
  "slides": [
    {
      "id": "slide-1",
      "type": "title",
      "content": {
        "title": "AI 产品介绍",
        "subtitle": "革命性的人工智能解决方案"
      },
      "orderIndex": 0
    }
  ],
  "slideCount": 1,
  "status": "draft",
  "version": 1,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

---

#### PUT /presentations/{id}
**描述**: 更新 PPT

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - PPT ID

**请求**:
```typescript
PresentationUpdate
```

**成功响应 (200)**:
```typescript
PresentationDetailResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新的标题",
    "status": "published"
  }'
```

---

#### DELETE /presentations/{id}
**描述**: 删除 PPT

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - PPT ID

**成功响应 (204)**: 无内容

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /presentations/{id}/slides
**描述**: 添加幻灯片

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - PPT ID

**请求**:
```typescript
SlideCreate
```

**成功响应 (201)**:
```typescript
PresentationDetailResponse  // 返回更新后的完整 PPT
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "content",
    "content": {
      "title": "新产品特性",
      "bullets": ["特性1", "特性2", "特性3"]
    },
    "position": 1
  }'
```

---

### Slides 模块

#### GET /presentations/{ppt_id}/slides
**描述**: 获取幻灯片列表

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID

**成功响应 (200)**:
```typescript
SlideResponse[]
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### GET /presentations/{ppt_id}/slides/{id}
**描述**: 获取单个幻灯片

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID
- `id` (string) - 幻灯片 ID

**成功响应 (200)**:
```typescript
SlideResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 幻灯片不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides/slide-1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### PUT /presentations/{ppt_id}/slides/{id}
**描述**: 更新幻灯片

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID
- `id` (string) - 幻灯片 ID

**请求**:
```typescript
SlideUpdate
```

**成功响应 (200)**:
```typescript
SlideResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 幻灯片不存在

**示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides/slide-1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "title": "更新的标题",
      "bullets": ["新特性1", "新特性2"]
    }
  }'
```

---

#### DELETE /presentations/{ppt_id}/slides/{id}
**描述**: 删除幻灯片

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID
- `id` (string) - 幻灯片 ID

**成功响应 (204)**: 无内容

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 幻灯片不存在

**示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides/slide-1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /presentations/{ppt_id}/slides/{id}/undo
**描述**: 撤销操作

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID
- `id` (string) - 幻灯片 ID

**成功响应 (200)**:
```typescript
UndoRedoResponse
```

**错误响应**:
- `400` CANNOT_UNDO - 无可撤销的操作
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides/slide-1/undo \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "success": true,
  "description": "撤销: 编辑幻灯片",
  "state": { ... },
  "slideId": "slide-1"
}
```

---

#### POST /presentations/{ppt_id}/slides/{id}/redo
**描述**: 重做操作

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `ppt_id` (string, UUID) - PPT ID
- `id` (string) - 幻灯片 ID

**成功响应 (200)**:
```typescript
UndoRedoResponse
```

**错误响应**:
- `400` CANNOT_REDO - 无可重做的操作
- `401` UNAUTHORIZED - 未认证

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/presentations/550e8400-e29b-41d4-a716-446655440000/slides/slide-1/redo \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Exports 模块

#### POST /exports/pptx
**描述**: 导出 PPTX

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
ExportRequest
```

**成功响应 (202)**:
```typescript
ExportResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/exports/pptx \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pptx",
    "quality": "high",
    "slideRange": "all",
    "includeNotes": false
  }'
```

**响应示例**:
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

#### POST /exports/pdf
**描述**: 导出 PDF

**请求头**:
```
Authorization: Bearer {accessToken}
```

**请求**:
```typescript
ExportRequest
```

**成功响应 (202)**:
```typescript
ExportResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - PPT 不存在

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/exports/pdf \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "quality": "high",
    "slideRange": "1-10",
    "includeNotes": true
  }'
```

---

#### GET /exports/{id}/status
**描述**: 查询导出状态

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 导出任务 ID

**成功响应 (200)**:
```typescript
ExportStatusResponse
```

**错误响应**:
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 任务不存在

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/exports/550e8400-e29b-41d4-a716-446655440000/status \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "presentationId": "550e8400-e29b-41d4-a716-446655440001",
  "format": "pptx",
  "status": "completed",
  "progress": 100,
  "fileSize": 1048576,
  "downloadUrl": "https://cdn.example.com/exports/550e8400-e29b-41d4-a716-446655440000.pptx",
  "expiresAt": "2024-01-08T00:00:00Z",
  "createdAt": "2024-01-01T00:00:00Z",
  "completedAt": "2024-01-01T00:01:30Z"
}
```

---

#### GET /exports/{id}/download
**描述**: 下载导出文件

**请求头**:
```
Authorization: Bearer {accessToken}
```

**路径参数**:
- `id` (string, UUID) - 导出任务 ID

**成功响应 (200)**: 文件流

**错误响应**:
- `400` NOT_COMPLETED - 导出任务尚未完成
- `401` UNAUTHORIZED - 未认证
- `404` NOT_FOUND - 任务或文件不存在
- `410` EXPIRED - 文件下载链接已过期

**示例**:
```bash
curl -X GET http://localhost:8000/api/v1/exports/550e8400-e29b-41d4-a716-446655440000/download \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --output presentation.pptx
```

---

### Charts 模块

#### ChartTypeEnum
```typescript
type ChartType = "bar" | "line" | "pie" | "scatter" | "area" | "radar" | "funnel" | "gauge" | "treemap" | "sunburst";
```

#### FieldTypeEnum
```typescript
type FieldType = "dimension" | "measure";
```

#### DataFieldType
```typescript
type DataFieldType = "string" | "number" | "date" | "boolean";
```

#### DataFieldInfo
```typescript
interface DataFieldInfo {
  name: string;                    // 字段名称
  fieldType: FieldType;            // 字段类型: dimension/measure
  dataType: DataFieldType;         // 数据类型: string/number/date/boolean
  uniqueCount: number;             // 唯一值数量
  nullCount: number;               // 空值数量
  sampleValues?: any[];            // 样本值列表
  minValue?: number;               // 最小值（数值字段）
  maxValue?: number;               // 最大值（数值字段）
  avgValue?: number;               // 平均值（数值字段）
}
```

#### DataAnalyzeRequest
```typescript
interface DataAnalyzeRequest {
  data: Record<string, any>[];     // 数据列表，minLength: 1
  sampleSize?: number;             // 采样大小，默认: 100
}
```

#### DataAnalyzeResponse
```typescript
interface DataAnalyzeResponse {
  totalRows: number;               // 总行数
  totalColumns: number;            // 总列数
  fields: DataFieldInfo[];         // 字段信息列表
  suggestions?: string[];          // 数据建议列表
}
```

#### FieldMapping
```typescript
interface FieldMapping {
  xField?: string;                 // X 轴字段
  yField?: string;                 // Y 轴字段
  seriesField?: string;            // 系列字段
  valueField?: string;             // 值字段（饼图等）
  nameField?: string;              // 名称字段
  sizeField?: string;              // 大小字段（散点图）
}
```

#### ChartStyleConfig
```typescript
interface ChartStyleConfig {
  title?: string;                  // 图表标题
  subtitle?: string;               // 图表副标题
  width?: number;                  // 图表宽度
  height?: number;                 // 图表高度
  colorPalette?: string[];         // 颜色调色板
  showLegend?: boolean;            // 是否显示图例，默认: true
  showTooltip?: boolean;           // 是否显示提示框，默认: true
  showGrid?: boolean;              // 是否显示网格，默认: true
  animation?: boolean;             // 是否启用动画，默认: true
  theme?: string;                  // 主题名称，默认: "default"
}
```

#### ChartGenerateRequest
```typescript
interface ChartGenerateRequest {
  chartType: ChartType;            // 图表类型
  data: Record<string, any>[];     // 数据列表，minLength: 1
  fieldMapping: FieldMapping;      // 字段映射配置
  styleConfig?: ChartStyleConfig;  // 样式配置
}
```

#### ChartGenerateResponse
```typescript
interface ChartGenerateResponse {
  chartType: ChartType;            // 图表类型
  echartsOption: Record<string, any>;  // ECharts 配置
  dataCount: number;               // 数据条数
  generatedAt: string;             // 生成时间，ISO 8601 datetime
}
```

#### RecommendedChart
```typescript
interface RecommendedChart {
  chartType: ChartType;            // 推荐图表类型
  confidence: number;              // 推荐置信度 (0.0 - 1.0)
  reason: string;                  // 推荐理由
  fieldMapping: FieldMapping;      // 建议的字段映射
  previewOption?: Record<string, any>;  // 预览配置（可选）
}
```

#### ChartRecommendRequest
```typescript
interface ChartRecommendRequest {
  data: Record<string, any>[];     // 数据列表，minLength: 1
  context?: string;                // 上下文描述（可选）
  maxRecommendations?: number;     // 最大推荐数量，范围: 1-5，默认: 3
}
```

#### ChartRecommendResponse
```typescript
interface ChartRecommendResponse {
  recommendations: RecommendedChart[];  // 推荐图表列表
  dataSummary: string;             // 数据摘要
  analyzedAt: string;              // 分析时间，ISO 8601 datetime
}
```

---

#### POST /charts/analyze
**描述**: 分析数据

**请求头**:
```
Content-Type: application/json
```

**请求**:
```typescript
DataAnalyzeRequest
```

**成功响应 (200)**:
```typescript
DataAnalyzeResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `500` INTERNAL_ERROR - 服务器错误

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/charts/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"category": "A", "value": 100, "date": "2024-01-01"},
      {"category": "B", "value": 200, "date": "2024-01-02"},
      {"category": "C", "value": 150, "date": "2024-01-03"}
    ],
    "sampleSize": 100
  }'
```

**响应示例**:
```json
{
  "totalRows": 3,
  "totalColumns": 3,
  "fields": [
    {
      "name": "category",
      "fieldType": "dimension",
      "dataType": "string",
      "uniqueCount": 3,
      "nullCount": 0,
      "sampleValues": ["A", "B", "C"]
    },
    {
      "name": "value",
      "fieldType": "measure",
      "dataType": "number",
      "uniqueCount": 3,
      "nullCount": 0,
      "minValue": 100,
      "maxValue": 200,
      "avgValue": 150
    },
    {
      "name": "date",
      "fieldType": "dimension",
      "dataType": "date",
      "uniqueCount": 3,
      "nullCount": 0,
      "sampleValues": ["2024-01-01", "2024-01-02", "2024-01-03"]
    }
  ],
  "suggestions": ["数据适合生成柱状图、折线图或饼图"]
}
```

---

#### POST /charts/generate
**描述**: 生成图表

**请求头**:
```
Content-Type: application/json
```

**请求**:
```typescript
ChartGenerateRequest
```

**成功响应 (200)**:
```typescript
ChartGenerateResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `500` INTERNAL_ERROR - 服务器错误

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/charts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "chartType": "bar",
    "data": [
      {"category": "A", "value": 100},
      {"category": "B", "value": 200},
      {"category": "C", "value": 150}
    ],
    "fieldMapping": {
      "xField": "category",
      "yField": "value"
    },
    "styleConfig": {
      "title": "销售数据",
      "showLegend": true,
      "animation": true
    }
  }'
```

**响应示例**:
```json
{
  "chartType": "bar",
  "echartsOption": {
    "title": {"text": "销售数据", "left": "center"},
    "tooltip": {"trigger": "axis"},
    "legend": {"orient": "horizontal", "bottom": 10},
    "xAxis": {"type": "category", "data": ["A", "B", "C"]},
    "yAxis": {"type": "value"},
    "series": [{"name": "value", "type": "bar", "data": [100, 200, 150]}]
  },
  "dataCount": 3,
  "generatedAt": "2024-01-01T00:00:00"
}
```

---

#### POST /charts/recommend
**描述**: 推荐图表

**请求头**:
```
Content-Type: application/json
```

**请求**:
```typescript
ChartRecommendRequest
```

**成功响应 (200)**:
```typescript
ChartRecommendResponse
```

**错误响应**:
- `400` INVALID_REQUEST - 参数错误
- `500` INTERNAL_ERROR - 服务器错误

**示例**:
```bash
curl -X POST http://localhost:8000/api/v1/charts/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"category": "A", "value": 100, "date": "2024-01-01"},
      {"category": "B", "value": 200, "date": "2024-01-02"},
      {"category": "C", "value": 150, "date": "2024-01-03"}
    ],
    "context": "销售数据分析",
    "maxRecommendations": 3
  }'
```

**响应示例**:
```json
{
  "recommendations": [
    {
      "chartType": "bar",
      "confidence": 0.9,
      "reason": "数据包含维度字段（category）和度量字段（value），适合使用柱状图展示对比关系",
      "fieldMapping": {
        "xField": "category",
        "yField": "value"
      }
    },
    {
      "chartType": "line",
      "confidence": 0.88,
      "reason": "数据包含时间维度（date），适合使用折线图展示趋势变化",
      "fieldMapping": {
        "xField": "date",
        "yField": "value"
      }
    },
    {
      "chartType": "pie",
      "confidence": 0.85,
      "reason": "维度字段（category）有 3 个唯一值，适合使用饼图展示占比分布",
      "fieldMapping": {
        "nameField": "category",
        "valueField": "value"
      }
    }
  ],
  "dataSummary": "共 3 行数据，3 个字段，2 个维度字段，1 个度量字段",
  "analyzedAt": "2024-01-01T00:00:00"
}
```

---

## 错误码定义

| 错误码 | 状态码 | 描述 |
|--------|--------|------|
| INVALID_REQUEST | 400 | 请求参数错误 |
| VALIDATION_ERROR | 422 | 验证失败 |
| INVALID_CREDENTIALS | 401 | 邮箱或密码错误 |
| UNAUTHORIZED | 401 | 未提供认证或认证无效 |
| TOKEN_EXPIRED | 401 | 令牌已过期 |
| INVALID_TOKEN | 401 | 无效的令牌 |
| USER_INACTIVE | 403 | 用户账户已被禁用 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| EMAIL_EXISTS | 409 | 邮箱已被注册 |
| USERNAME_EXISTS | 409 | 用户名已被使用 |
| NAME_EXISTS | 409 | 名称已存在 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMITED | 429 | 请求过于频繁 |
| CONNECTION_FAILED | 502 | 数据源连接失败 |
| QUERY_FAILED | 502 | 查询执行失败 |
| NOT_IMPLEMENTED | 501 | 功能尚未实现 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| NOT_COMPLETED | 400 | 任务尚未完成 |
| EXPIRED | 410 | 资源已过期 |
| CANNOT_UNDO | 400 | 无可撤销的操作 |
| CANNOT_REDO | 400 | 无可重做的操作 |
| INVALID_QUERY | 400 | 查询语法错误 |

---

## 变更日志

### v1.3 (2026-02-15)
- 新增 Charts 模块（数据可视化）
- 新增 `POST /charts/analyze` 数据分析端点
- 新增 `POST /charts/generate` 图表生成端点
- 新增 `POST /charts/recommend` 图表推荐端点
- 新增 `ChartType`, `FieldType`, `DataFieldType` 类型
- 新增 `DataFieldInfo`, `DataAnalyzeRequest`, `DataAnalyzeResponse` 类型
- 新增 `FieldMapping`, `ChartStyleConfig`, `ChartGenerateRequest`, `ChartGenerateResponse` 类型
- 新增 `RecommendedChart`, `ChartRecommendRequest`, `ChartRecommendResponse` 类型
- 支持柱状图、折线图、饼图、散点图、面积图、雷达图、漏斗图等图表类型

### v1.2 (2026-02-15)
- 新增 Chat 模块（AI 提示词助手）
- 新增 `POST /chat` 聊天端点，支持流式响应 (SSE)
- 新增 `POST /chat/analyze` 意图分析端点
- 新增 `ChatMessage`, `ChatContext`, `ChatRequest`, `ChatResponse`, `ChatResponseChunk` 类型
- 新增 `IntentType`, `IntentAnalysis` 类型

### v1.1 (2026-02-15)
- 新增 `PUT /auth/me` 更新用户信息接口
- 新增 `POST /auth/me/avatar` 上传头像接口
- User 类型新增 `avatar` 可选字段
- 新增 `UpdateUserRequest` 类型
- 新增 `AvatarUploadResponse` 类型

### v1.0 (2026-02-12)
- 初始版本
- 包含完整的 Auth, Connectors, Outlines, Presentations, Slides, Exports 模块
- 定义所有 TypeScript 类型接口
- 包含完整的 curl 测试示例
- 定义完整的错误码体系

---

## ⚠️ 强制更新规则

1. **新增端点**：必须先更新此文档，再实现代码
2. **修改字段**：必须更新此文档，同步前后端
3. **删除端点**：必须标记为 DEPRECATED，保留 2 个版本
4. **类型变更**：必须同步更新 TypeScript 和 Python 类型
5. **错误码变更**：必须在错误码定义表中添加并说明变更原因

### 违反规则后果
- 前后端不兼容
- 测试失败
- 功能回滚

### 文档更新流程
1. 创建 PR 更新 API_CONTRACT.md
2. 前后端团队同时审查
3. 通过后更新各自的类型定义
4. 实现代码并测试
5. 合并后更新变更日志
