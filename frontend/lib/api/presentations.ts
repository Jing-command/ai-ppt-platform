// lib/api/presentations.ts
// PPT API 客户端 - 对应 API_CONTRACT.md Presentations 模块

import {
  PresentationCreate,
  PresentationUpdate,
  PresentationResponse,
  PresentationDetailResponse,
  SlideCreate,
  SlideUpdate,
  Slide,
  GeneratePresentationRequest,
  GeneratePresentationResponse,
  PresentationListParams,
  PaginatedResponse,
  UndoRedoResponse,
  ExportRequest,
  ExportResponse
} from '@/types/presentation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/**
 * 获取认证头
 */
function getAuthHeaders(): HeadersInit {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`
  };
}

/**
 * 处理 API 响应
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: '请求失败',
      code: 'UNKNOWN_ERROR'
    }));
    throw new Error(error.message || '请求失败');
  }
  return response.json();
}

/**
 * 获取 PPT 列表
 */
export async function getPresentations(
  params: PresentationListParams = {}
): Promise<PaginatedResponse<PresentationResponse>> {
  const searchParams = new URLSearchParams();
  if (params.page) { searchParams.set('page', params.page.toString()); }
  if (params.pageSize) { searchParams.set('pageSize', params.pageSize.toString()); }
  if (params.status) { searchParams.set('status', params.status); }

  const response = await fetch(`${API_BASE}/api/v1/presentations?${searchParams}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(response);
}

/**
 * 获取 PPT 详情
 */
export async function getPresentation(id: string): Promise<PresentationDetailResponse> {
  const response = await fetch(`${API_BASE}/api/v1/presentations/${id}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(response);
}

/**
 * 创建 PPT
 */
export async function createPresentation(
  data: PresentationCreate
): Promise<PresentationDetailResponse> {
  const response = await fetch(`${API_BASE}/api/v1/presentations`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  return handleResponse(response);
}

/**
 * 更新 PPT
 */
export async function updatePresentation(
  id: string,
  data: PresentationUpdate
): Promise<PresentationDetailResponse> {
  const response = await fetch(`${API_BASE}/api/v1/presentations/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  return handleResponse(response);
}

/**
 * 删除 PPT
 */
export async function deletePresentation(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/presentations/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({message: '删除失败'}));
    throw new Error(error.message || '删除失败');
  }
}

/**
 * AI 生成 PPT
 */
export async function generatePresentation(
  data: GeneratePresentationRequest
): Promise<GeneratePresentationResponse> {
  const response = await fetch(`${API_BASE}/api/v1/presentations/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  return handleResponse(response);
}

/**
 * 添加幻灯片
 */
export async function addSlide(
  presentationId: string,
  slideData: SlideCreate
): Promise<PresentationDetailResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/presentations/${presentationId}/slides`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(slideData)
    }
  );
  return handleResponse(response);
}

/**
 * 更新幻灯片
 */
export async function updateSlide(
  presentationId: string,
  slideId: string,
  data: SlideUpdate
): Promise<Slide> {
  const response = await fetch(
    `${API_BASE}/api/v1/presentations/${presentationId}/slides/${slideId}`,
    {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    }
  );
  return handleResponse(response);
}

/**
 * 删除幻灯片
 */
export async function deleteSlide(
  presentationId: string,
  slideId: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/v1/presentations/${presentationId}/slides/${slideId}`,
    {
      method: 'DELETE',
      headers: getAuthHeaders()
    }
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({message: '删除失败'}));
    throw new Error(error.message || '删除失败');
  }
}

/**
 * 撤销操作
 */
export async function undoSlide(
  presentationId: string,
  slideId: string
): Promise<UndoRedoResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/presentations/${presentationId}/slides/${slideId}/undo`,
    {
      method: 'POST',
      headers: getAuthHeaders()
    }
  );
  return handleResponse(response);
}

/**
 * 重做操作
 */
export async function redoSlide(
  presentationId: string,
  slideId: string
): Promise<UndoRedoResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/presentations/${presentationId}/slides/${slideId}/redo`,
    {
      method: 'POST',
      headers: getAuthHeaders()
    }
  );
  return handleResponse(response);
}

/**
 * 导出 PPT
 */
export async function exportPresentation(
  presentationId: string,
  data: ExportRequest
): Promise<ExportResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/exports/${data.format}`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        presentationId,
        ...data
      })
    }
  );
  return handleResponse(response);
}
