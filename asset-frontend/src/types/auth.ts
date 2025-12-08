/**
 * OAuth 2.0 인증 관련 타입 정의
 * Backend API와 일치하는 타입 구조
 */

export interface LoginRequest {
  grant_type: 'password';
  username: string;
  password: string;
  device_type?: 'web' | 'ios' | 'android';
  device_id?: string;
}

export interface RefreshTokenRequest {
  grant_type: 'refresh_token';
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_expires_in: number;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  phone_number?: string;
  receive_daily_report?: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  phone_number?: string;
  receive_daily_report: boolean;
}

export interface UserInfoResponse {
  sub: string;
  username: string;
  email?: string;
  phone_number?: string;
  email_verified: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
