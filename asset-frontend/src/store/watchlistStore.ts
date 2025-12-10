import { create } from 'zustand';
import { watchlistService, Watchlist, WatchlistAsset } from '../services/watchlistService';
import { toastUtils } from '../utils/toast';

interface WatchlistState {
  watchlists: Watchlist[];
  selectedWatchlist: Watchlist | null;
  watchlistAssets: WatchlistAsset[];
  isLoading: boolean;
  fetchWatchlists: () => Promise<void>;
  createWatchlist: (name: string) => Promise<void>;
  updateWatchlist: (id: number, name: string) => Promise<void>;
  deleteWatchlist: (id: number) => Promise<void>;
  fetchWatchlistAssets: (id: number) => Promise<void>;
  selectWatchlist: (watchlist: Watchlist | null) => void;
}

export const useWatchlistStore = create<WatchlistState>((set, get) => ({
  watchlists: [],
  selectedWatchlist: null,
  watchlistAssets: [],
  isLoading: false,

  fetchWatchlists: async () => {
    set({ isLoading: true });
    try {
      const watchlists = await watchlistService.getWatchlists();
      set({ watchlists, isLoading: false });
    } catch (error) {
      toastUtils.error('Failed to fetch watchlists.');
      set({ isLoading: false });
    }
  },

  createWatchlist: async (name: string) => {
    try {
      const newWatchlist = await watchlistService.createWatchlist(name);
      set((state) => ({ watchlists: [...state.watchlists, newWatchlist] }));
      toastUtils.success(`Watchlist "${name}" created.`);
    } catch (error) {
      toastUtils.error('Failed to create watchlist.');
    }
  },

  updateWatchlist: async (id: number, name: string) => {
    try {
      const updatedWatchlist = await watchlistService.updateWatchlist(id, name);
      set((state) => ({
        watchlists: state.watchlists.map((w) => (w.id === id ? updatedWatchlist : w)),
      }));
      toastUtils.success(`Watchlist updated to "${name}".`);
    } catch (error) {
      toastUtils.error('Failed to update watchlist.');
    }
  },

  deleteWatchlist: async (id: number) => {
    try {
      await watchlistService.deleteWatchlist(id);
      set((state) => ({
        watchlists: state.watchlists.filter((w) => w.id !== id),
      }));
      toastUtils.success('Watchlist deleted.');
    } catch (error) {
      toastUtils.error('Failed to delete watchlist.');
    }
  },

  fetchWatchlistAssets: async (id: number) => {
    set({ isLoading: true });
    try {
      const assets = await watchlistService.getWatchlistAssets(id);
      set({ watchlistAssets: assets, isLoading: false });
    } catch (error) {
      toastUtils.error('Failed to fetch watchlist assets.');
      set({ isLoading: false });
    }
  },

  selectWatchlist: (watchlist: Watchlist | null) => {
    set({ selectedWatchlist: watchlist, watchlistAssets: [] });
    if (watchlist) {
      get().fetchWatchlistAssets(watchlist.id);
    }
  },
}));
