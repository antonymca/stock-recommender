'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { Plus, TrendingUp, TrendingDown, DollarSign, Target } from 'lucide-react'
import toast from 'react-hot-toast'

interface Position {
  id: string
  ticker: string
  shares: number
  avgPrice: number
  currentPrice: number
  totalValue: number
  totalReturn: number
  returnPercent: number
}

interface Portfolio {
  id: string
  name: string
  totalValue: number
  totalReturn: number
  returnPercent: number
  positions: Position[]
}

export default function PortfolioPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddPosition, setShowAddPosition] = useState(false)
  const [newPosition, setNewPosition] = useState({
    ticker: '',
    shares: '',
    avgPrice: ''
  })

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
      return
    }
    if (session) {
      fetchPortfolios()
    }
  }, [session, status])

  const fetchPortfolios = async () => {
    try {
      // Mock portfolio data - replace with real API
      const mockPortfolios: Portfolio[] = [
        {
          id: '1',
          name: 'Main Portfolio',
          totalValue: 125430.50,
          totalReturn: 15430.50,
          returnPercent: 14.05,
          positions: [
            {
              id: '1',
              ticker: 'AAPL',
              shares: 100,
              avgPrice: 150.00,
              currentPrice: 175.43,
              totalValue: 17543.00,
              totalReturn: 2543.00,
              returnPercent: 16.95
            },
            {
              id: '2',
              ticker: 'MSFT',
              shares: 50,
              avgPrice: 300.00,
              currentPrice: 378.85,
              totalValue: 18942.50,
              totalReturn: 3942.50,
              returnPercent: 26.28
            },
            {
              id: '3',
              ticker: 'GOOGL',
              shares: 75,
              avgPrice: 120.00,
              currentPrice: 142.56,
              totalValue: 10692.00,
              totalReturn: 1692.00,
              returnPercent: 18.80
            }
          ]
        }
      ]
      
      setPortfolios(mockPortfolios)
      setSelectedPortfolio(mockPortfolios[0])
    } catch (error) {
      console.error('Error fetching portfolios:', error)
      toast.error('Failed to load portfolios')
    } finally {
      setLoading(false)
    }
  }

  const addPosition = async () => {
    if (!newPosition.ticker || !newPosition.shares || !newPosition.avgPrice) {
      toast.error('Please fill in all fields')
      return
    }

    try {
      // Mock adding position - replace with real API
      const position: Position = {
        id: Date.now().toString(),
        ticker: newPosition.ticker.toUpperCase(),
        shares: parseFloat(newPosition.shares),
        avgPrice: parseFloat(newPosition.avgPrice),
        currentPrice: parseFloat(newPosition.avgPrice) * (1 + Math.random() * 0.2 - 0.1), // Mock current price
        totalValue: 0,
        totalReturn: 0,
        returnPercent: 0
      }

      position.totalValue = position.shares * position.currentPrice
      position.totalReturn = position.totalValue - (position.shares * position.avgPrice)
      position.returnPercent = (position.totalReturn / (position.shares * position.avgPrice)) * 100

      if (selectedPortfolio) {
        const updatedPortfolio = {
          ...selectedPortfolio,
          positions: [...selectedPortfolio.positions, position]
        }
        setSelectedPortfolio(updatedPortfolio)
        setPortfolios(prev => prev.map(p => p.id === selectedPortfolio.id ? updatedPortfolio : p))
      }

      setNewPosition({ ticker: '', shares: '', avgPrice: '' })
      setShowAddPosition(false)
      toast.success('Position added successfully')
    } catch (error) {
      console.error('Error adding position:', error)
      toast.error('Failed to add position')
    }
  }

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin w-12 h-12 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      </div>
    )
  }

  if (!session) return null

  const pieData = selectedPortfolio?.positions.map(pos => ({
    name: pos.ticker,
    value: pos.totalValue,
    color: `hsl(${Math.random() * 360}, 70%, 50%)`
  })) || []

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Portfolio Management</h1>
            <p className="text-gray-400">Track and manage your investment portfolio</p>
          </div>
          <button
            onClick={() => setShowAddPosition(true)}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Add Position</span>
          </button>
        </div>

        {selectedPortfolio && (
          <>
            {/* Portfolio Overview */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <DollarSign className="text-blue-400" size={24} />
                  <span className="text-green-400 text-sm">+2.3%</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                  ${selectedPortfolio.totalValue.toLocaleString()}
                </div>
                <div className="text-gray-400 text-sm">Total Value</div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="text-green-400" size={24} />
                  <span className="text-green-400 text-sm">Today</span>
                </div>
                <div className="text-2xl font-bold text-green-400 mb-1">
                  +${selectedPortfolio.totalReturn.toLocaleString()}
                </div>
                <div className="text-gray-400 text-sm">Total Return</div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <Target className="text-purple-400" size={24} />
                  <span className="text-green-400 text-sm">+{selectedPortfolio.returnPercent.toFixed(2)}%</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                  {selectedPortfolio.positions.length}
                </div>
                <div className="text-gray-400 text-sm">Positions</div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <TrendingDown className="text-orange-400" size={24} />
                  <span className="text-gray-400 text-sm">Risk</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">Medium</div>
                <div className="text-gray-400 text-sm">Risk Level</div>
              </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-8 mb-8">
              {/* Portfolio Allocation */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Portfolio Allocation</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1f2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                        formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Performance Chart */}
              <div className="lg:col-span-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Performance by Position</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={selectedPortfolio.positions}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="ticker" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" tickFormatter={(value) => `${value}%`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1f2937',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                        formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
                      />
                      <Bar dataKey="returnPercent" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Positions Table */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-xl font-semibold text-white">Positions</h2>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Symbol</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Shares</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Avg Price</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Current Price</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Total Value</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Return</th>
                      <th className="px-6 py-4 text-left text-sm font-medium text-gray-300">Return %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {selectedPortfolio.positions.map((position) => (
                      <tr key={position.id} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-medium text-white">{position.ticker}</div>
                        </td>
                        <td className="px-6 py-4 text-white">{position.shares}</td>
                        <td className="px-6 py-4 text-white">${position.avgPrice.toFixed(2)}</td>
                        <td className="px-6 py-4 text-white">${position.currentPrice.toFixed(2)}</td>
                        <td className="px-6 py-4 text-white">${position.totalValue.toLocaleString()}</td>
                        <td className="px-6 py-4">
                          <span className={position.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}>
                            {position.totalReturn >= 0 ? '+' : ''}${position.totalReturn.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={position.returnPercent >= 0 ? 'text-green-400' : 'text-red-400'}>
                            {position.returnPercent >= 0 ? '+' : ''}{position.returnPercent.toFixed(2)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Add Position Modal */}
        {showAddPosition && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-white/10 rounded-xl p-6 w-full max-w-md mx-4">
              <h3 className="text-xl font-semibold text-white mb-6">Add New Position</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Stock Ticker</label>
                  <input
                    type="text"
                    placeholder="e.g., AAPL"
                    value={newPosition.ticker}
                    onChange={(e) => setNewPosition(prev => ({ ...prev, ticker: e.target.value.toUpperCase() }))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Number of Shares</label>
                  <input
                    type="number"
                    placeholder="100"
                    value={newPosition.shares}
                    onChange={(e) => setNewPosition(prev => ({ ...prev, shares: e.target.value }))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Average Price</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="150.00"
                    value={newPosition.avgPrice}
                    onChange={(e) => setNewPosition(prev => ({ ...prev, avgPrice: e.target.value }))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-4 mt-6">
                <button
                  onClick={addPosition}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all"
                >
                  Add Position
                </button>
                <button
                  onClick={() => setShowAddPosition(false)}
                  className="flex-1 bg-white/10 border border-white/20 text-white py-3 rounded-lg font-medium hover:bg-white/20 transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}