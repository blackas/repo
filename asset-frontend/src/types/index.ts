export type AssetType = 'kr-stock' | 'us-stock' | 'crypto';

export interface Asset {
  id: string | number;
  name: string;
  symbol?: string;
  currentPrice?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
  [key: string]: any;
}

export interface AssetDetail extends Asset {
  description?: string;
  sector?: string;
  industry?: string;
  historicalData?: PriceData[];
}

export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface AssetState {
  items: Asset[];
  isLoading: boolean;
  error: string | null;
}

export interface StoreState {
  auth: {
    user: string | null;
    token: string | null;
  };
  assets: {
    [key in AssetType]: AssetState;
  };
  setAssets: (assetType: AssetType, assets: Asset[]) => void;
  setLoading: (assetType: AssetType, isLoading: boolean) => void;
  setError: (assetType: AssetType, error: string | null) => void;
  setAuth: (user: string | null, token: string | null) => void;
}
