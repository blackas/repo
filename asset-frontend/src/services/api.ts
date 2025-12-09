import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import type { AssetType, Asset, AssetDetail } from '../types';
import { tokenStorage } from '../utils/tokenStorage';
import { authService } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 갱신 중인지 추적
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

// 토큰 갱신 완료 시 대기 중인 요청들에게 알림
function onRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

// 토큰 갱신 대기 큐에 추가
function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

// Request interceptor - Access Token 추가
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - 401 에러 시 토큰 갱신
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 에러이고, 재시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 인증 관련 엔드포인트는 즉시 로그인 페이지로
      if (
        originalRequest.url?.includes('/auth/token') ||
        originalRequest.url?.includes('/auth/userinfo')
      ) {
        tokenStorage.clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      // 이미 토큰 갱신 중이면 대기
      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        const refreshToken = tokenStorage.getRefreshToken();

        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        // Refresh Token으로 새 Access Token 발급
        const tokenResponse = await authService.refreshToken(refreshToken);

        // 새 토큰 저장
        tokenStorage.setTokens(tokenResponse);

        // 대기 중인 요청들에게 알림
        onRefreshed(tokenResponse.access_token);

        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${tokenResponse.access_token}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Refresh Token도 만료됨 -> 로그아웃
        tokenStorage.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Get endpoint based on asset type
const getEndpointForAssetType = (assetType: AssetType): string => {
  const endpointMap: Record<string, string> = {
    'kr-stock': '/stocks',
    'us-stock': '/stocks',
    'crypto': '/crypto',
  };
  return endpointMap[assetType];
};

// API Functions
export const apiService = {
  // Get list of assets by type
  getAssets: async (assetType: AssetType, params?: Record<string, any>): Promise<any> => {
    const endpoint = getEndpointForAssetType(assetType);
    const response = await axiosInstance.get(endpoint, { params });
    return response.data;
  },

  // Get asset detail by type and ID
  getAssetDetail: async (assetType: AssetType, assetId: string | number): Promise<AssetDetail> => {
    const endpoint = getEndpointForAssetType(assetType);
    const response = await axiosInstance.get(`${endpoint}/${assetId}`);
    return response.data;
  },

  // Get asset prices by type and ID
  getAssetPrices: async (assetType: AssetType, assetId: string | number, params?: Record<string, any>): Promise<any> => {
    const endpoint = getEndpointForAssetType(assetType);
    const response = await axiosInstance.get(`${endpoint}/${assetId}/prices`, { params });
    return response.data;
  },
};

export default axiosInstance;
