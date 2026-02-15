// lib/api/exports.ts
// 导出 API 客户端 - 对应 API_CONTRACT.md Exports 模块

import {
    ExportResponse,
    ExportStatusResponse
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

export interface PptxExportOptions {
  presentationId: string;
  quality?: 'standard' | 'high';
  slideRange?: string;
  includeNotes?: boolean;
}

export interface PdfExportOptions {
  presentationId: string;
  quality?: 'standard' | 'high';
  slideRange?: string;
  includeNotes?: boolean;
}

export interface ImagesExportOptions {
  presentationId: string;
  format?: 'png' | 'jpg';
  quality?: 'standard' | 'high';
  slideRange?: string;
}

/**
 * 导出为 PPTX
 */
export async function exportPptx(options: PptxExportOptions): Promise<ExportResponse> {
    const params = new URLSearchParams();
    params.set('presentation_id', options.presentationId);
    if (options.quality) { params.set('quality', options.quality); }
    if (options.slideRange) { params.set('slide_range', options.slideRange); }
    if (options.includeNotes) { params.set('include_notes', 'true'); }

    const response = await fetch(`${API_BASE}/api/v1/exports/pptx?${params}`, {
        method: 'POST',
        headers: getAuthHeaders()
    });
    return handleResponse(response);
}

/**
 * 导出为 PDF
 */
export async function exportPdf(options: PdfExportOptions): Promise<ExportResponse> {
    const params = new URLSearchParams();
    params.set('presentation_id', options.presentationId);
    if (options.quality) { params.set('quality', options.quality); }
    if (options.slideRange) { params.set('slide_range', options.slideRange); }
    if (options.includeNotes) { params.set('include_notes', 'true'); }

    const response = await fetch(`${API_BASE}/api/v1/exports/pdf?${params}`, {
        method: 'POST',
        headers: getAuthHeaders()
    });
    return handleResponse(response);
}

/**
 * 导出为图片
 */
export async function exportImages(options: ImagesExportOptions): Promise<ExportResponse> {
    const params = new URLSearchParams();
    params.set('presentation_id', options.presentationId);
    params.set('format', options.format || 'png');
    if (options.quality) { params.set('quality', options.quality); }
    if (options.slideRange) { params.set('slide_range', options.slideRange); }

    const response = await fetch(`${API_BASE}/api/v1/exports/images?${params}`, {
        method: 'POST',
        headers: getAuthHeaders()
    });
    return handleResponse(response);
}

/**
 * 查询导出状态
 */
export async function getExportStatus(taskId: string): Promise<ExportStatusResponse> {
    const response = await fetch(`${API_BASE}/api/v1/exports/${taskId}/status`, {
        headers: getAuthHeaders()
    });
    return handleResponse(response);
}

/**
 * 下载导出文件
 */
export async function downloadExport(taskId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/api/v1/exports/${taskId}/download`, {
        headers: {
            Authorization: `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('accessToken') : ''}`
        }
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({
            message: '下载失败',
            code: 'DOWNLOAD_ERROR'
        }));
        throw new Error(error.message || '下载失败');
    }

    return response.blob();
}
