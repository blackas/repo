import axios, { type AxiosInstance } from 'axios';
import type { AssetType, Asset, AssetDetail } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Get endpoint based on asset type
const getEndpointForAssetType = (assetType: AssetType): string => {
  const endpointMap: Record<AssetType, string> = {
    'kr-stock': '/stocks/kr',
    'us-stock': '/stocks/us',
    'crypto': '/crypto',
  };
  return endpointMap[assetType] || '/stocks/kr';
};

// API Functions
export const apiService = {
  // Get list of assets by type
  getAssets: async (assetType: AssetType, params?: Record<string, any>): Promise<Asset[]> => {
    const endpoint = getEndpointForAssetType(assetType);
    const response = await axiosInstance.get(endpoint, { params });
    return response.data.results || response.data;
  },

  // Get asset detail by type and ID
  getAssetDetail: async (assetType: AssetType, assetId: string | number): Promise<AssetDetail> => {
    const endpoint = getEndpointForAssetType(assetType);
    const response = await axiosInstance.get(`${endpoint}/${assetId}`);
    return response.data;
  },

  // Search assets across types
  searchAssets: async (query: string, assetType?: AssetType): Promise<Asset[]> => {
    if (assetType) {
      const endpoint = getEndpointForAssetType(assetType);
      const response = await axiosInstance.get(`${endpoint}/search`, { params: { q: query } });
      return response.data.results || response.data;
    }
    // Search across all types
    const response = await axiosInstance.get('/search', { params: { q: query } });
    return response.data.results || response.data;
  },

  // Get reports for an asset
  getReports: async (assetType: AssetType, assetId: string | number) => {
    const response = await axiosInstance.get(`/reports`, {
      params: { asset_type: assetType, asset_id: assetId },
    });
    return response.data.results || response.data;
  },

  // Get dashboard summary
  getDashboardSummary: async () => {
    const response = await axiosInstance.get('/dashboard/summary');
    return response.data;
  },
};

export default axiosInstance;
