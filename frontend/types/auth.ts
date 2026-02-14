/**
 * @fileoverview 认证相关类型定义
 * @author Frontend Agent
 * @date 2026-02-14
 */

/** 用户基础信息 */
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

/** 登录请求 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 登录响应 */
export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

/** 注册请求 */
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

/** 注册响应 */
export interface RegisterResponse {
  id: string;
  email: string;
  name: string;
  created_at: string;
}
