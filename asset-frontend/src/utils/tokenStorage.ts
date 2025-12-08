/**
 * 토큰 저장소 유틸리티
 * localStorage를 사용한 토큰 관리
 */

import type { TokenResponse } from '../types/auth';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';

export const tokenStorage = {
  /**
   * Access Token 저장
   * 만료 시간을 계산하여 함께 저장 (60초 버퍼)
   */
  setAccessToken(token: string, expiresIn: number): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);

    // 만료 시간 계산 (현재 시간 + expiresIn - 60초 버퍼)
    const expiryTime = Date.now() + (expiresIn - 60) * 1000;
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
  },

  /**
   * Access Token 가져오기
   */
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /**
   * Refresh Token 저장
   */
  setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  /**
   * Refresh Token 가져오기
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  /**
   * 토큰 만료 확인
   * 60초 버퍼를 고려하여 만료 여부 판단
   */
  isTokenExpired(): boolean {
    const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!expiryTime) return true;

    return Date.now() >= parseInt(expiryTime);
  },

  /**
   * 모든 토큰 삭제 (로그아웃 시)
   */
  clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
  },

  /**
   * 토큰 저장 (access + refresh)
   * TokenResponse를 받아서 토큰들을 저장
   */
  setTokens(tokenResponse: TokenResponse): void {
    this.setAccessToken(tokenResponse.access_token, tokenResponse.expires_in);
    this.setRefreshToken(tokenResponse.refresh_token);
  },

  /**
   * 토큰 존재 여부 확인
   */
  hasTokens(): boolean {
    return !!(this.getAccessToken() && this.getRefreshToken());
  },
};
