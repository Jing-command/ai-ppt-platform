import { apiClient } from './client';
import { LoginRequest, LoginResponse, User } from '@/types/auth';

// localStorage keys
const TOKEN_KEY = 'accessToken';
const USER_KEY = 'user';

/**
 * 用户登录
 * @param credentials 登录凭证
 * @returns 登录响应
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
  return response.data;
}

/**
 * 保存认证信息到 localStorage
 * @param data 登录响应数据
 */
export function saveAuthData(data: LoginResponse): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, data.accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  }
}

/**
 * 获取存储的 accessToken
 * @returns token 字符串或 null
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * 获取存储的用户信息
 * @returns User 对象或 null
 */
export function getUser(): User | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr) as User;
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * 清除认证信息（登出）
 */
export function clearAuthData(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * 检查用户是否已登录
 * @returns boolean
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
