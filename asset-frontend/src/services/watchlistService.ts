import axiosInstance from './api';

export interface Watchlist {
  id: number;
  name: string;
  user_id: number;
}

export interface WatchlistAsset {
  id: number;
  asset_type: string;
  symbol: string;
}

export const watchlistService = {
  async getWatchlists(): Promise<Watchlist[]> {
    const response = await axiosInstance.get<Watchlist[]>('/watchlists');
    return response.data;
  },

  async createWatchlist(name: string): Promise<Watchlist> {
    const response = await axiosInstance.post<Watchlist>('/watchlists', { name });
    return response.data;
  },

  async updateWatchlist(id: number, name: string): Promise<Watchlist> {
    const response = await axiosInstance.patch<Watchlist>(`/watchlists/${id}`, { name });
    return response.data;
  },

  async deleteWatchlist(id: number): Promise<void> {
    await axiosInstance.delete(`/watchlists/${id}`);
  },

  async getWatchlistAssets(id: number): Promise<WatchlistAsset[]> {
    const response = await axiosInstance.get<WatchlistAsset[]>(`/watchlists/${id}/assets`);
    return response.data;
  },

  async addAssetToWatchlist(watchlistId: number, assetType: string, assetId: number): Promise<void> {
    await axiosInstance.post(`/watchlists/${watchlistId}/assets`, { asset_type: assetType, asset_id: assetId });
  },

  async removeAssetFromWatchlist(watchlistId: number, assetId: number): Promise<void> {
    await axiosInstance.delete(`/watchlists/${watchlistId}/assets/${assetId}`);
  },
};
