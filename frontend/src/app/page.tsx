'use client'

import { useState, useEffect } from 'react'
import StockSearch from '@/components/StockSearch'
import StockScreener from '@/components/StockScreener'
import LoginForm from '@/components/LoginForm'

interface Signal {
  ticker: string
  signal: string
  score: number
  price?: number
  reason: string
}

interface User {
  username: string
  email: string
}

export default function Dashboard() {
  const [signals, setSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'search' | 'screener'>('dashboard')

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/signals`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      setSignals(data)
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch signals')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (userData: User) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  const handleSignalUpdate = (newSignal: Signal) => {
    setSignals(prev => {
      const existing = prev.findIndex(s => s.ticker === newSignal.ticker)
      if (existing >= 0) {
        const updated = [...prev]
        updated[existing] = newSignal
        return updated
      }
      return [newSignal, ...prev]
    })
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-700 bg-green-100 border-green-200'
      case 'SELL': return 'text-red-700 bg-red-100 border-red-200'
      default: return 'text-yellow-700 bg-yellow-100 border-yellow-200'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score <= 0.3) return 'text-red-600'
    return 'text-yellow-600'
  }

  if (!user) {
    return <LoginForm onLogin={handleLogin} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Stock Recommender</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.username}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'search', label: 'Stock Search', icon: '🔍' },
              { id: 'screener', label: 'Stock Screener', icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-500'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-blue-600 text-xl">📊</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Signals</p>
                    <p className="text-2xl font-semibold text-gray-900">{signals.length}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-green-600 text-xl">📈</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Buy Signals</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {signals.filter(s => s.signal === 'BUY').length}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <span className="text-red-600 text-xl">📉</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Sell Signals</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {signals.filter(s => s.signal === 'SELL').length}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <span className="text-yellow-600 text-xl">⏸️</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Hold Signals</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {signals.filter(s => s.signal === 'HOLD').length}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading stock signals...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-center">
                  <span className="text-red-500 text-xl mr-3">⚠️</span>
                  <div>
                    <h3 className="text-red-800 font-semibold">Connection Error</h3>
                    <p className="text-red-700 mt-1">{error}</p>
                  </div>
                </div>
                <button
                  onClick={fetchSignals}
                  className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Signals Grid */}
            {!loading && !error && signals.length > 0 && (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {signals.map((signal, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold text-gray-900">{signal.ticker}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getSignalColor(signal.signal)}`}>
                        {signal.signal}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Confidence Score:</span>
                        <div className="flex items-center">
                          <span className={`font-semibold ${getScoreColor(signal.score)}`}>
                            {(signal.score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      
                      {/* Score Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            signal.score >= 0.7 ? 'bg-green-500' : 
                            signal.score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${signal.score * 100}%` }}
                        ></div>
                      </div>
                      
                      {signal.price && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Current Price:</span>
                          <span className="font-semibold text-lg">${signal.price.toFixed(2)}</span>
                        </div>
                      )}
                      
                      <div className="mt-4 p-3 bg-gray-50 rounded-md">
                        <p className="text-sm text-gray-700 leading-relaxed">{signal.reason}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && signals.length === 0 && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <span className="text-6xl mb-4 block">📊</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No signals available</h3>
                <p className="text-gray-600 mb-6">Try searching for specific stocks or check back later</p>
                <button
                  onClick={fetchSignals}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Refresh Signals
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'search' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Individual Stocks</h2>
              <StockSearch onSignalUpdate={handleSignalUpdate} />
            </div>
          </div>
        )}

        {activeTab === 'screener' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Stock Screener</h2>
              <StockScreener />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
