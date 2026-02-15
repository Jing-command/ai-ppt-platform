/**
 * @fileoverview 认证 API 模块
 * @author Frontend Agent
 * @date 2026-02-14
 */

import {apiClient} from './client';
import {
  AvatarUploadResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UpdateUserRequest,
  User,
} from '@/types/auth';

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
 * 用户注册
 * @param data 注册信息
 * @returns 注册响应
 */
export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const response = await apiClient.post<RegisterResponse>('/auth/register', data);
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

/**
 * 更新用户信息
 * @param data 用户更新信息
 * @returns 更新后的用户信息
 */
export async function updateUser(data: UpdateUserRequest): Promise<User> {
  const response = await apiClient.put<User>('/auth/me', data);
  // 更新本地存储的用户信息
  const currentUser = getUser();
  if (currentUser) {
    const updatedUser = {...currentUser, ...response.data};
    localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
  }
  return response.data;
}

/**
 * 上传头像
 * @param file 头像文件
 * @returns 上传后的头像URL
 */
export async function uploadAvatar(file: File): Promise<AvatarUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<AvatarUploadResponse>('/auth/me/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  // 更新本地存储的用户信息
  const currentUser = getUser();
  if (currentUser) {
    const updatedUser = {...currentUser, avatar: response.data.avatarUrl};
    localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
  }
  return response.data;
}

/**
 * 更新本地存储的用户信息
 * @param user 用户信息
 */
export function updateStoredUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}
