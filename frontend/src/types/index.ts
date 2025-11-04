export interface MarketPrice {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  timestamp: string
}

export interface MarketOverview {
  total_market_cap: number
  btc_dominance: number
  eth_dominance: number
  defi_market_cap: number
  total_volume_24h: number
  fear_greed_index?: number
}

export interface FearGreedIndex {
  value: number
  value_classification: string
  timestamp: string
  time_until_update?: number
}

export interface TradingSignal {
  symbol: string
  signal: 'buy' | 'sell' | 'hold'
  confidence: number
  entry_price: number
  stop_loss: number
  take_profit: number
  strategy: string
  timestamp: string
  reasons: string[]
}

export interface Position {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  entry_price: number
  current_price: number
  amount: number
  value_usd: number
  pnl: number
  pnl_percentage: number
  stop_loss?: number
  take_profit?: number
  opened_at: string
}

export interface PortfolioSummary {
  total_value: number
  available_balance: number
  positions_value: number
  total_pnl: number
  total_pnl_percentage: number
  open_positions: number
  today_pnl: number
  win_rate: number
}

export interface StrategyConfig {
  name: string
  enabled: boolean
  pairs: string[]
  timeframe: string
  max_open_trades: number
  stake_amount: number
  stop_loss: number
  take_profit: number
  trailing_stop: boolean
  use_ml: boolean
  use_sentiment: boolean
  min_confidence: number
}
