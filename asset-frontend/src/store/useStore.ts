import { create } from 'zustand';
import type { StoreState, AssetType, Asset } from '../types';

const useStore = create<StoreState>((set) => ({
  auth: {
    user: null,
    token: localStorage.getItem('authToken'),
  },
  assets: {
    'kr-stock': {
      items: [],
      isLoading: false,
      error: null,
    },
    'us-stock': {
      items: [],
      isLoading: false,
      error: null,
    },
    'crypto': {
      items: [],
      isLoading: false,
      error: null,
    },
  },
  setAssets: (assetType: AssetType, assets: Asset[]) =>
    set((state) => ({
      assets: {
        ...state.assets,
        [assetType]: {
          ...state.assets[assetType],
          items: assets,
        },
      },
    })),
  setLoading: (assetType: AssetType, isLoading: boolean) =>
    set((state) => ({
      assets: {
        ...state.assets,
        [assetType]: {
          ...state.assets[assetType],
          isLoading,
        },
      },
    })),
  setError: (assetType: AssetType, error: string | null) =>
    set((state) => ({
      assets: {
        ...state.assets,
        [assetType]: {
          ...state.assets[assetType],
          error,
        },
      },
    })),
  setAuth: (user: string | null, token: string | null) => {
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
    set({ auth: { user, token } });
  },
}));

export default useStore;
