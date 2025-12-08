/**
 * 인증 관련 API 서비스
 * 순환 참조를 피하기 위해 axios를 직접 import하여 사용
 */

import axios from 'axios';
import type {
  LoginRequest,
  RefreshTokenRequest,
  TokenResponse,
  RegisterRequest,
  User,
  UserInfoResponse,
} from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';

// authService 전용 axios 인스턴스 (순환 참조 방지)
const authAxios = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  /**
   * 로그인 (OAuth 2.0 Password Grant)
   */
  async login(username: string, password: string): Promise<TokenResponse> {
    const request: LoginRequest = {
      grant_type: 'password',
      username,
      password,
      device_type: 'web',
      device_id: `web-${Date.now()}`,
    };

    const response = await authAxios.post<TokenResponse>('/auth/token', request);
    return response.data;
  },

  /**
   * Refresh Token으로 Access Token 갱신
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const request: RefreshTokenRequest = {
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    };

    const response = await authAxios.post<TokenResponse>('/auth/token', request);
    return response.data;
  },

  /**
   * 회원가입
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await authAxios.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * 현재 사용자 정보 가져오기 (OIDC UserInfo)
   */
  async getUserInfo(accessToken: string): Promise<UserInfoResponse> {
    const response = await authAxios.get<UserInfoResponse>('/auth/userinfo', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  },

  /**
   * 로그아웃 (서버에 토큰 무효화 요청)
   */
  async logout(accessToken: string): Promise<void> {
    await authAxios.post(
      '/auth/logout',
      {},
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
  },

  /**
   * 토큰 무효화
   */
  async revokeToken(token: string): Promise<void> {
    await authAxios.post('/auth/revoke', {
      token,
      token_type_hint: 'refresh_token',
    });
  },
};
