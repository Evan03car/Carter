import axios from 'axios';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

const api = axios.create({
  baseURL: `${API_URL}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

// Types
export interface MarketplaceItem {
  item_id: string;
  title: string;
  price: number;
  estimated_resale_price?: number;
  profit_margin?: number;
  platform: string;
  url?: string;
  image_url?: string;
  location?: string;
  category?: string;
  demand_level?: string;
  best_resell_platform?: string;
}

export interface DealAlert {
  alert_id?: string;
  category: string;
  min_profit_margin: number;
  location?: string;
  push_token?: string;
  active: boolean;
}

export interface PriceEstimate {
  estimated_price: number;
  confidence: string;
  demand_level: string;
  best_platform: string;
  analysis: string;
}