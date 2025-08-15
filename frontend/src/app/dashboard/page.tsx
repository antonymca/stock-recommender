'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface StockData {
  ticker: string
  signal: string
  score: number
  price: number
  reason: string
  change: number
  changePercent: number
}

export default function Dashboard() {
  const [stocks, setStocks] = useState<StockData[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTicker, setSearchTicker] = useState('')

  useEffect(() => {
    fetchStockData()
  }, [])

  const fetchStockData = async () => {
    try {
      // Mock data for now - replace with actual API calls
      const mockData: StockData[] = [
        { ticker: 'AAPL', signal: 'BUY', score: 0.85, price: 175.43, reason: 'Strong technical indicators', change: 2.34, changePercent: 1.35 },
        { ticker: 'MSFT', signal: 'HOLD', score: 0.72, price: 378.85, reason: 'Consolidating near resistance', change: -1.23, changePercent: -0.32 },
        { ticker: 'GOOGL', signal: 'BUY', score: 0.78, price: 142.56, reason: 'Bullish momentum building', change: 3.45, changePercent: 2.48 },
        { ticker: 'TSLA', signal: 'SELL', score: 0.45, price: 248.42, reason: 'Bearish divergence detected', change: -5.67, changePercent: -2.23 },
      ]
      setStocks(mockData)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching stock data:', error)
      setLoading(false)
    }
  }

  const analyzeStock = async () => {
    if (!searchTicker) return
    
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/signals/${searchTicker}`)
      const data = await response.json()
      setStocks(prev => [data, ...prev.filter(s => s.ticker !== data.ticker)])
    } catch (error) {
      console.error('Error analyzing stock:', error)
    }
    setLoading(false)
    setSearchTicker('')
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-400 bg-green-400/10'
      case 'SELL': return 'text-red-400 bg-red-400/10'
      case 'HOLD': return 'text-yellow-400 bg-yellow-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">SR</span>
            </div>
            <span className="text-white font-semibold text-xl">Stock Recommender</span>
          </Link>
          <div className="flex items-center space-x-6">
            <Link href="/dashboard" className="text-white font-medium">Dashboard</Link>
            <Link href="/portfolio" className="text-gray-300 hover:text-white transition-colors">Portfolio</Link>
            <Link href="/insights" className="text-gray-300 hover:text-white transition-colors">Insights</Link>
            <Link href="/reports" className="text-gray-300 hover:text-white transition-colors">Reports</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Stock Analysis Dashboard</h1>
          <p className="text-gray-400">Real-time AI-powered stock recommendations and insights</p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="flex gap-4 max-w-md">
            <input
              type="text"
              placeholder="Enter stock ticker (e.g., AAPL)"
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
              className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && analyzeStock()}
            />
            <button
              onClick={analyzeStock}
              disabled={!searchTicker || loading}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Analyzed', value: stocks.length, color: 'from-blue-500 to-cyan-500' },
            { label: 'Buy Signals', value: stocks.filter(s => s.signal === 'BUY').length, color: 'from-green-500 to-emerald-500' },
            { label: 'Sell Signals', value: stocks.filter(s => s.signal === 'SELL').length, color: 'from-red-500 to-pink-500' },
            { label: 'Avg Score', value: (stocks.reduce((acc, s) => acc + s.score, 0) / stocks.length || 0).toFixed(2), color: 'from-purple-500 to-indigo-500' },
          ].map((stat, index) => (
            <div key={index} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
                <span className="text-white font-bold">📊</span>
              </div>
              <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-gray-400 text-sm">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Stock Analysis Table */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10">
            <h2 className="text-xl font-semibold text-white">Stock Analysis Results</h2>
          </div>
          
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-gray-400">Analyzing stocks...</p>
            </div>
          ) : stocks.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-400 mb-4">No stocks analyzed yet</p>
              <p className="text-sm text-gray-500">Enter a ticker symbol above to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Ticker</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Price</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Change</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Signal</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Score</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Reason</th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {stocks.map((stock, index) => (
                    <tr key={index} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-white">{stock.ticker}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-white">${stock.price.toFixed(2)}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSignalColor(stock.signal)}`}>
                          {stock.signal}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-700 rounded-full h-2 mr-3">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                              style={{ width: `${stock.score * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-white text-sm">{(stock.score * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-gray-300 text-sm max-w-xs truncate">{stock.reason}</div>
                      </td>
                      <td className="px-6 py-4">
                        <Link 
                          href={`/analysis/${stock.ticker}`}
                          className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                        >
                          View Details →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}