// types/presentation.ts
// PPT 类型定义 - 对应 API_CONTRACT.md Presentations 模块

/**
 * 幻灯片类型
 */
export type SlideType = 'title' | 'content' | 'section' | 'chart' | 'conclusion';

/**
 * PPT 状态
 */
export type PresentationStatus = 'draft' | 'generating' | 'completed' | 'published' | 'archived';

/**
 * 幻灯片内容
 */
export interface SlideContent {
  title?: string;
  subtitle?: string;
  description?: string;
  text?: string;
  secondColumn?: string;
  bullets?: string[];
  imageUrl?: string;
  chartData?: Record<string, any>;
  stats?: Record<string, any>[];
  events?: Record<string, any>[];
  steps?: string[];
  items?: Record<string, any>[];
  left?: Record<string, any>;
  right?: Record<string, any>;
  quote?: string;
  author?: string;
}

/**
 * 幻灯片布局
 */
export interface SlideLayout {
  type: 'title' | 'content' | 'split' | 'image' | 'chart' | 'timeline' | 'data' | 'quote';
  background?: string;
  theme?: string;
}

/**
 * 幻灯片样式
 */
export interface SlideStyle {
  fontFamily?: string;
  fontSize?: number;
  color?: string;
  alignment?: string;
}

/**
 * 幻灯片
 */
export interface Slide {
  id: string;
  type: SlideType;
  content: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  orderIndex: number;
  imagePrompt?: string;
}

/**
 * 创建 PPT 请求
 */
export interface PresentationCreate {
  title: string;
  description?: string;
  templateId?: string;
  outlineId?: string;
  slides?: Slide[];
}

/**
 * 更新 PPT 请求
 */
export interface PresentationUpdate {
  title?: string;
  description?: string;
  slides?: Slide[];
  status?: PresentationStatus;
  templateId?: string;
}

/**
 * PPT 响应（列表）
 */
export interface PresentationResponse {
  id: string;
  title: string;
  description?: string;
  slideCount: number;
  status: PresentationStatus;
  outlineId?: string;
  templateId?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * PPT 详情响应
 */
export interface PresentationDetailResponse {
  id: string;
  title: string;
  description?: string;
  userId: string;
  slides: Slide[];
  slideCount: number;
  status: PresentationStatus;
  outlineId?: string;
  templateId?: string;
  version: number;
  aiPrompt?: string;
  aiParameters?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

/**
 * 创建幻灯片请求
 */
export interface SlideCreate {
  type?: SlideType;
  content: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  position?: number;
}

/**
 * 更新幻灯片请求
 */
export interface SlideUpdate {
  type?: SlideType;
  content?: SlideContent;
  layout?: SlideLayout;
  style?: SlideStyle;
  notes?: string;
  orderIndex?: number;
}

/**
 * AI 生成 PPT 请求
 */
export interface GeneratePresentationRequest {
  prompt: string;
  templateId?: string;
  numSlides?: number;
  language?: 'zh' | 'en';
  style?: 'business' | 'education' | 'creative' | 'minimal';
  provider?: string;
}

/**
 * AI 生成 PPT 响应
 */
export interface GeneratePresentationResponse {
  taskId: string;
  status: string;
  estimatedTime: number;
  message: string;
}

/**
 * 撤销/重做响应
 */
export interface UndoRedoResponse {
  success: boolean;
  description: string;
  state?: Record<string, any>;
  slideId?: string;
}

/**
 * PPT 列表查询参数
 */
export interface PresentationListParams {
  page?: number;
  pageSize?: number;
  status?: PresentationStatus;
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
 * 导出请求
 */
export interface ExportRequest {
  format: 'pptx' | 'pdf' | 'png' | 'jpg';
  quality?: 'standard' | 'high';
  slideRange?: string;
  includeNotes?: boolean;
}

/**
 * 导出响应
 */
export interface ExportResponse {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  fileSize?: number;
  expiresAt?: string;
  createdAt: string;
}

/**
 * 导出状态响应
 */
export interface ExportStatusResponse {
  taskId: string;
  presentationId: string;
  format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  filePath?: string;
  fileSize?: number;
  errorMessage?: string;
  downloadUrl?: string;
  expiresAt?: string;
  createdAt: string;
  completedAt?: string;
}
