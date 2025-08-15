'use client'

import { useState } from 'react'

interface Signal {
  ticker: string
  signal: string
  score: number
  price?: number
  reason: string
}

interface StockSearchProps {
  onSignalUpdate: (signal: Signal) => void
}

export default function StockSearch({ onSignalUpdate }: StockSearchProps) {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [lastSearched, setLastSearched] = useState('')

  const popularStocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']

  const handleSearch = async (searchTicker?: string) => {
    const targetTicker = searchTicker || ticker
    if (!targetTicker.trim()) return

    setLoading(true)
    setError('')
    setLastSearched(targetTicker.toUpperCase())

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/signals/${targetTicker.toUpperCase()}`)
      
      if (!response.ok) {
        throw new Error('Stock not found or API error')
      }
      
      const signal = await response.json()
      onSignalUpdate(signal)
      
      if (!searchTicker) {
        setTicker('')
      }
    } catch (err) {
      setError('Failed to fetch stock signal. Please check the ticker symbol and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSearch()
  }

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-2">
            Stock Ticker Symbol
          </label>
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                id="ticker"
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Enter ticker (e.g., AAPL, MSFT, GOOGL)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                disabled={loading}
                maxLength={10}
              />
              {error && <p className="text-red-500 text-sm mt-2 flex items-center">
                <span className="mr-1">⚠️</span>
                {error}
              </p>}
            </div>
            <button
              type="submit"
              disabled={loading || !ticker.trim()}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </div>
              ) : (
                '🔍 Analyze'
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Popular Stocks */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Popular Stocks</h3>
        <div className="flex flex-wrap gap-2">
          {popularStocks.map((stock) => (
            <button
              key={stock}
              onClick={() => handleSearch(stock)}
              disabled={loading}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 disabled:opacity-50 transition-colors text-sm font-medium"
            >
              {stock}
            </button>
          ))}
        </div>
      </div>

      {/* Search History */}
      {lastSearched && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-blue-600 mr-2">📊</span>
            <span className="text-sm text-blue-700">
              Last analyzed: <strong>{lastSearched}</strong>
            </span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">How to use:</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Enter a stock ticker symbol (e.g., AAPL for Apple Inc.)</li>
          <li>• Click "Analyze" or press Enter to get AI-powered recommendations</li>
          <li>• Use popular stock buttons for quick analysis</li>
          <li>• Results will appear in the main dashboard</li>
        </ul>
      </div>
    </div>
  )
}
