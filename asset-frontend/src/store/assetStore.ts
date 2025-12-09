import { create } from 'zustand';
import type { Asset, AssetType, AssetState } from '../types';
import { toastUtils } from '../utils/toast';

type AssetStore = {
  [key in AssetType]: AssetState;
};

interface AssetActions {
  setAssets: (assetType: AssetType, assets: Asset[]) => void;
  setLoading: (assetType: AssetType, isLoading: boolean) => void;
  setError: (assetType: AssetType, error: string | null) => void;
}

const createAssetSlice = (assetType: AssetType) => ({
  [assetType]: {
    items: [],
    isLoading: false,
    error: null,
  },
});

const useAssetStore = create<AssetStore & AssetActions>((set) => ({
  ...createAssetSlice('kr-stock'),
  ...createAssetSlice('us-stock'),
  ...createAssetSlice('crypto'),

  setAssets: (assetType, assets) =>
    set((state) => ({
      [assetType]: { ...state[assetType], items: assets, isLoading: false },
    })),

  setLoading: (assetType, isLoading) =>
    set((state) => ({
      [assetType]: { ...state[assetType], isLoading },
    })),

  setError: (assetType, error) => {
    set((state) => ({
      [assetType]: { ...state[assetType], error, isLoading: false },
    }));
    if (error) {
      toastUtils.error(error);
    }
  },
}));

export default useAssetStore;
