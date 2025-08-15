'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Activity, Globe, Zap } from 'lucide-react'

interface MarketInsight {
  id: string
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  category: 'market' | 'sector' | 'economic' | 'technical'
  timestamp: string
}

interface SectorPerformance {
  sector: string
  performance: number
  volume: number
  marketCap: string
}

export default function InsightsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [insights, setInsights] = useState<MarketInsight[]>([])
  const [sectorData, setSectorData] = useState<SectorPerformance[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
      return
    }
    if (session) {
      fetchInsights()
      fetchSectorData()
    }
  }, [session, status])

  const fetchInsights = async () => {
    try {
      const mockInsights: MarketInsight[] = [
        {
          id: '1',
          title: 'Tech Sector Rally Continues',
          description: 'Technology stocks are showing strong momentum with AI-related companies leading the charge. NVIDIA and Microsoft are key drivers.',
          impact: 'high',
          category: 'sector',
          timestamp: '2 hours ago'
        },
        {
          id: '2',
          title: 'Federal Reserve Policy Impact',
          description: 'Recent Fed statements suggest potential rate cuts in Q2 2024, which could benefit growth stocks and real estate.',
          impact: 'high',
          category: 'economic',
          timestamp: '4 hours ago'
        },
        {
          id: '3',
          title: 'Energy Sector Volatility',
          description: 'Oil prices fluctuation creating opportunities in energy stocks. Consider defensive positions.',
          impact: 'medium',
          category: 'sector',
          timestamp: '6 hours ago'
        },
        {
          id: '4',
          title: 'Market Technical Analysis',
          description: 'S&P 500 approaching key resistance level at 4,800. Breakout could signal continued bull market.',
          impact: 'medium',
          category: 'technical',
          timestamp: '8 hours ago'
        }
      ]
      
      setInsights(mockInsights)
    } catch (error) {
      console.error('Error fetching insights:', error)
    }
  }

  const fetchSectorData = async () => {
    try {
      const mockSectorData: SectorPerformance[] = [
        { sector: 'Technology', performance: 12.5, volume: 2500000000, marketCap: '$15.2T' },
        { sector: 'Healthcare', performance: 8.3, volume: 1200000000, marketCap: '$8.7T' },
        { sector: 'Financial', performance: 6.7, volume: 1800000000, marketCap: '$9.1T' },
        { sector: 'Consumer Disc.', performance: 5.2, volume: 900000000, marketCap: '$6.3T' },
        { sector: 'Energy', performance: -2.1, volume: 800000000, marketCap: '$4.2T' },
        { sector: 'Utilities', performance: 3.4, volume: 400000000, marketCap: '$3.8T' },
        { sector: 'Real Estate', performance: 4.8, volume: 300000000, marketCap: '$2.9T' },
        { sector: 'Materials', performance: 1.9, volume: 600000000, marketCap: '$3.5T' }
      ]
      
      setSectorData(mockSectorData)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching sector data:', error)
      setLoading(false)
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

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-400 bg-red-400/10'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10'
      case 'low': return 'text-green-400 bg-green-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'market': return Globe
      case 'sector': return Activity
      case 'economic': return DollarSign
      case 'technical': return Zap
      default: return Activity
    }
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Market Insights</h1>
          <p className="text-gray-400">AI-powered market analysis and sector performance</p>
        </div>

        {/* Market Overview Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="text-green-400" size={24} />
              <span className="text-green-400 text-sm">+2.3%</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">4,785</div>
            <div className="text-gray-400 text-sm">S&P 500</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <DollarSign className="text-blue-400" size={24} />
              <span className="text-red-400 text-sm">-0.8%</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">15,234</div>
            <div className="text-gray-400 text-sm">NASDAQ</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Activity className="text-purple-400" size={24} />
              <span className="text-green-400 text-sm">+1.2%</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">37,892</div>
            <div className="text-gray-400 text-sm">Dow Jones</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Globe className="text-orange-400" size={24} />
              <span className="text-yellow-400 text-sm">Neutral</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">65</div>
            <div className="text-gray-400 text-sm">VIX</div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Sector Performance */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Sector Performance</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sectorData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9ca3af" tickFormatter={(value) => `${value}%`} />
                  <YAxis type="category" dataKey="sector" stroke="#9ca3af" width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, 'Performance']}
                  />
                  <Bar dataKey="performance" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Market Cap Distribution */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Market Cap Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sectorData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="performance"
                    label={({ sector, performance }) => `${sector}: ${performance.toFixed(1)}%`}
                  >
                    {sectorData.map((entry, index) => (
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
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Market Insights */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Latest Market Insights</h2>
          <div className="space-y-4">
            {insights.map((insight) => {
              const IconComponent = getCategoryIcon(insight.category)
              return (
                <div key={insight.id} className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <IconComponent size={20} className="text-white" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-medium text-white">{insight.title}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact)}`}>
                            {insight.impact.toUpperCase()}
                          </span>
                          <span className="text-gray-400 text-sm">{insight.timestamp}</span>
                        </div>
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed">{insight.description}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
