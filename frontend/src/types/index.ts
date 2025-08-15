export interface StockData {
  ticker: string
  companyName: string
  price: number
  change: number
  changePercent: number
  signal: 'BUY' | 'SELL' | 'HOLD'
  score: number
  volume: number
  marketCap?: string
}

export interface Portfolio {
  id: string
  name: string
  totalValue: number
  totalReturn: number
  positions: PortfolioPosition[]
  createdAt: string
  updatedAt: string
}

export interface PortfolioPosition {
  id: string
  ticker: string
  shares: number
  avgPrice: number
  currentPrice: number
  totalValue: number
  totalReturn: number
}

export interface Watchlist {
  id: string
  name: string
  tickers: string[]
  createdAt: string
  updatedAt: string
}

export interface PriceAlert {
  id: string
  ticker: string
  targetPrice: number
  condition: 'above' | 'below'
  isActive: boolean
  triggered: boolean
  createdAt: string
}

export interface MarketInsight {
  id: string
  title: string
  description: string
  category: string
  impact: 'high' | 'medium' | 'low'
  timestamp: string
}