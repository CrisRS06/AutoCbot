import axios from 'axios'
import type {
  MarketPrice,
  MarketOverview,
  FearGreedIndex,
  TradingSignal,
  Position,
  PortfolioSummary,
  StrategyConfig,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Market Data
export const marketApi = {
  getOverview: () => api.get<MarketOverview>('/market/overview'),
  getPrices: (symbols: string) => api.get<MarketPrice[]>(`/market/prices?symbols=${symbols}`),
  getPrice: (symbol: string) => api.get<MarketPrice>(`/market/price/${symbol}`),
  getCandles: (symbol: string, timeframe: string, limit: number = 100) =>
    api.get(`/market/candles/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  getTrending: (limit: number = 10) => api.get(`/market/trending?limit=${limit}`),
  getGainersLosers: (limit: number = 10) => api.get(`/market/gainers-losers?limit=${limit}`),
}

// Sentiment
export const sentimentApi = {
  getFearGreed: () => api.get<FearGreedIndex>('/sentiment/fear-greed'),
  getSocialSentiment: (symbol: string) => api.get(`/sentiment/social/${symbol}`),
  getAnalysis: (symbols?: string) =>
    api.get(`/sentiment/analysis${symbols ? `?symbols=${symbols}` : ''}`),
}

// Trading
export const tradingApi = {
  getSignals: (symbols?: string) =>
    api.get<TradingSignal[]>(`/trading/signals${symbols ? `?symbols=${symbols}` : ''}`),
  getSignal: (symbol: string) => api.get<TradingSignal>(`/trading/signal/${symbol}`),
  createOrder: (data: any) => api.post('/trading/order', data),
  getOrders: (status: string = 'open') => api.get(`/trading/orders?status=${status}`),
  cancelOrder: (orderId: string) => api.delete(`/trading/order/${orderId}`),
  closeAllPositions: () => api.post('/trading/close-all'),
}

// Portfolio
export const portfolioApi = {
  getSummary: () => api.get<PortfolioSummary>('/portfolio/summary'),
  getPositions: () => api.get<Position[]>('/portfolio/positions'),
  getPosition: (symbol: string) => api.get<Position>(`/portfolio/position/${symbol}`),
  getHistory: (days: number = 30) => api.get(`/portfolio/history?days=${days}`),
  getPerformance: () => api.get('/portfolio/performance'),
  getPnLChart: (days: number = 30) => api.get(`/portfolio/pnl-chart?days=${days}`),
}

// Strategy
export const strategyApi = {
  list: () => api.get<StrategyConfig[]>('/strategy/list'),
  get: (name: string) => api.get<StrategyConfig>(`/strategy/${name}`),
  create: (config: StrategyConfig) => api.post<StrategyConfig>('/strategy/', config),
  toggle: (name: string) => api.put(`/strategy/${name}/toggle`),
  delete: (name: string) => api.delete(`/strategy/${name}`),
  runBacktest: (data: any) => api.post('/strategy/backtest', data),
  getBacktestResults: (limit: number = 10) => api.get(`/strategy/backtest/results?limit=${limit}`),
}

export default api
