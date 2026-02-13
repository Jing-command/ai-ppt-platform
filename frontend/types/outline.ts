// types/outline.ts
// 大纲类型定义 - 对应 API_CONTRACT.md Outlines 模块

/**
 * 页面类型
 */
export type PageType = "title" | "content" | "section" | "chart" | "conclusion";

/**
 * 背景类型
 */
export type BackgroundType = "ai" | "upload" | "solid";

/**
 * PPT背景设置
 */
export interface OutlineBackground {
  type: BackgroundType;
  prompt?: string;      // AI生成背景时的提示词
  url?: string;         // 上传图片的URL
  color?: string;       // 纯色背景的颜色值 (hex)
  opacity?: number;     // 背景透明度 (0-1)，默认1
  blur?: number;        // 背景模糊度 (0-20px)，默认0
}

/**
 * 大纲页面（每页PPT的内容）
 */
export interface OutlineSection {
  id: string;
  pageNumber: number;
  title: string;
  content?: string;
  pageType?: PageType;
  layout?: string;
  notes?: string;
  imagePrompt?: string; // 插图提示词
}

/**
 * 大纲基础信息
 */
export interface OutlineBase {
  title: string;
  description?: string;
}

/**
 * 创建大纲请求
 */
export interface OutlineCreate extends OutlineBase {
  pages?: OutlineSection[];
  background?: OutlineBackground;
}

/**
 * 更新大纲请求
 */
export interface OutlineUpdate {
  title?: string;
  description?: string;
  pages?: OutlineSection[];
  background?: OutlineBackground;
}

/**
 * 大纲状态
 */
export type OutlineStatus = "draft" | "generating" | "completed" | "archived";

/**
 * 大纲响应
 */
export interface OutlineResponse extends OutlineBase {
  id: string;
  userId: string;
  pages: OutlineSection[];
  background?: OutlineBackground;
  totalSlides: number;
  status: OutlineStatus;
  aiPrompt?: string;
  aiParameters?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  generatedAt?: string;
}

/**
 * 大纲详情响应
 */
export type OutlineDetailResponse = OutlineResponse;

/**
 * AI 生成大纲请求
 */
export interface OutlineGenerateRequest {
  prompt: string;
  numSlides?: number;  // 总页数，默认15，范围3-50
  language?: "zh" | "en";
  style?: "business" | "education" | "creative" | "technical";
  contextData?: Record<string, any>;
  connectorId?: string;
}

/**
 * AI 生成大纲响应
 */
export interface OutlineGenerateResponse {
  taskId: string;
  status: "pending" | "processing" | "completed" | "failed";
  estimatedTime: number;
  message: string;
}

/**
 * 大纲转 PPT 请求
 */
export interface OutlineToPresentationRequest {
  title?: string;
  templateId?: string;
  theme?: string;
  slideLayout?: "auto" | "detailed" | "minimal";
  generateContent?: boolean;
  provider?: string;
}

/**
 * 大纲转 PPT 响应
 */
export interface OutlineToPresentationResponse {
  presentationId: string;
  taskId: string;
  status: string;
  message: string;
  estimatedTime: number;
}

/**
 * 大纲列表查询参数
 */
export interface OutlineListParams {
  page?: number;
  pageSize?: number;
  status?: OutlineStatus;
}

/**
 * 分页响应
 */
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

/**
 * 文件上传响应
 */
export interface UploadResponse {
  url: string;
  filename: string;
  size: number;
}
