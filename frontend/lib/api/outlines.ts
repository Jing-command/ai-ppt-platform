// lib/api/outlines.ts
// 大纲 API 客户端 - 对应 API_CONTRACT.md Outlines 模块

import {
  OutlineCreate,
  OutlineUpdate,
  OutlineResponse,
  OutlineDetailResponse,
  OutlineGenerateRequest,
  OutlineGenerateResponse,
  OutlineToPresentationRequest,
  OutlineToPresentationResponse,
  OutlineListParams,
  PaginatedResponse,
} from "@/types/outline";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

/**
 * 获取认证头
 */
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("accessToken");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

/**
 * 处理 API 响应
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: "请求失败",
      code: "UNKNOWN_ERROR",
    }));
    throw new Error(error.message || "请求失败");
  }
  return response.json();
}

/**
 * 获取大纲列表
 */
export async function getOutlines(
  params: OutlineListParams = {}
): Promise<PaginatedResponse<OutlineResponse>> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", params.page.toString());
  if (params.pageSize) searchParams.set("pageSize", params.pageSize.toString());
  if (params.status) searchParams.set("status", params.status);

  const response = await fetch(`${API_BASE}/api/v1/outlines?${searchParams}`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * 获取大纲详情
 */
export async function getOutline(id: string): Promise<OutlineDetailResponse> {
  const response = await fetch(`${API_BASE}/api/v1/outlines/${id}`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * 创建大纲
 */
export async function createOutline(
  data: OutlineCreate
): Promise<OutlineResponse> {
  const response = await fetch(`${API_BASE}/api/v1/outlines`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * 更新大纲
 */
export async function updateOutline(
  id: string,
  data: OutlineUpdate
): Promise<OutlineResponse> {
  const response = await fetch(`${API_BASE}/api/v1/outlines/${id}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * 删除大纲
 */
export async function deleteOutline(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/outlines/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "删除失败" }));
    throw new Error(error.message || "删除失败");
  }
}

/**
 * AI 生成大纲
 */
export async function generateOutline(
  data: OutlineGenerateRequest
): Promise<OutlineGenerateResponse> {
  const response = await fetch(`${API_BASE}/api/v1/outlines/generate`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * 基于大纲创建 PPT
 */
export async function createPresentationFromOutline(
  outlineId: string,
  data: OutlineToPresentationRequest = {}
): Promise<OutlineToPresentationResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/outlines/${outlineId}/presentations`,
    {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }
  );
  return handleResponse(response);
}
