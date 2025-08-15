'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter, useParams } from 'next/navigation'
import Navbar from '@/components/Navbar'
import StockChart from '@/components/StockChart'
import { TrendingUp, TrendingDown, Target, AlertTriangle, Star, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'

interface StockAnalysis {
  ticker: string
  companyName: string
  price: number
  change: number
  changePercent: number
  signal: string
  score: number
  targetPrice: number
  riskLevel: string
  technicalIndicators: {
    rsi: number
    macd: number
    sma20: number
    sma50: number
    volume: number
  }
  fundamentals: {
    pe: number
    eps: number
    marketCap: string
    dividend: number
    beta: number
  }
  recommendations: string[]
  news: Array<{
    title: string
    summary: string
    timestamp: string
    sentiment: 'positive' | 'negative' | 'neutral'
  }>
}

export default function AnalysisPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const params = useParams()
  const ticker = params.ticker as string
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [watchlisted, setWatchlisted] = useState(false)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
      return
    }
    if (session && ticker) {
      fetchAnalysis()
    }
  }, [session, status, ticker])

  const fetchAnalysis = async () => {
    try {
      // Mock detailed analysis
      const mockAnalysis: StockAnalysis = {
        ticker: ticker.toUpperCase(),
        companyName: `${ticker.toUpperCase()} Corporation`,
        price: 175.43,
        change: 2.34,
        changePercent: 1.35,
        signal: 'BUY',
        score: 0.85,
        targetPrice: 195.00,
        riskLevel: 'Medium',
        technicalIndicators: {
          rsi: 65.4,
          macd: 1.23,
          sma20: 172.50,
          sma50: 168.30,
          volume: 45234567
        },
        fundamentals: {
          pe: 28.5,
          eps: 6.15,
          marketCap: '$2.8T',
          dividend: 0.96,
          beta: 1.2
        },
        recommendations: [
          'Strong technical momentum with RSI in bullish territory',
          'Price above both 20-day and 50-day moving averages',
          'High trading volume indicates strong investor interest',
          'Consider taking profits near $195 target price'
        ],
        news: [
          {
            title: 'Company Reports Strong Q4 Earnings',
            summary: 'Quarterly earnings exceeded expectations with strong revenue growth',
            timestamp: '2 hours ago',
            sentiment: 'positive'
          },
          {
            title: 'Analyst Upgrades Price Target',
            summary: 'Major investment firm raises price target to $200',
            timestamp: '4 hours ago',
            sentiment: 'positive'
          },
          {
            title: 'Market Volatility Concerns',
            summary: 'General market uncertainty may impact stock performance',
            timestamp: '6 hours ago',
            sentiment: 'neutral'
          }
        ]
      }
      
      setAnalysis(mockAnalysis)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching analysis:', error)
      toast.error('Failed to load analysis')
      setLoading(false)
    }
  }

  const toggleWatchlist = () => {
    setWatchlisted(!watchlisted)
    toast.success(watchlisted ? 'Removed from watchlist' : 'Added to watchlist')
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

  if (!session || !analysis) return null

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-400 bg-green-400/10'
      case 'SELL': return 'text-red-400 bg-red-400/10'
      case 'HOLD': return 'text-yellow-400 bg-yellow-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400'
      case 'negative': return 'text-red-400'
      case 'neutral': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link 
              href="/dashboard"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft size={24} />
            </Link>
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                {analysis.ticker} - {analysis.companyName}
              </h1>
              <div className="flex items-center space-x-4">
                <span className="text-3xl font-bold text-white">${analysis.price.toFixed(2)}</span>
                <span className={`text-xl ${analysis.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {analysis.change >= 0 ? '+' : ''}{analysis.change.toFixed(2)} ({analysis.changePercent.toFixed(2)}%)
                </span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSignalColor(analysis.signal)}`}>
                  {analysis.signal}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={toggleWatchlist}
            className={`p-3 rounded-lg transition-colors ${
              watchlisted 
                ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
                : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-yellow-400'
            }`}
          >
            <Star size={24} fill={watchlisted ? 'currentColor' : 'none'} />
          </button>
        </div>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Target className="text-blue-400" size={24} />
              <span className="text-green-400 text-sm">+11.2%</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">${analysis.targetPrice.toFixed(2)}</div>
            <div className="text-gray-400 text-sm">Price Target</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="text-green-400" size={24} />
              <div className="w-16 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                  style={{ width: `${analysis.score * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{(analysis.score * 100).toFixed(0)}%</div>
            <div className="text-gray-400 text-sm">AI Score</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <AlertTriangle className="text-orange-400" size={24} />
              <span className="text-orange-400 text-sm">{analysis.riskLevel}</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{analysis.fundamentals.beta}</div>
            <div className="text-gray-400 text-sm">Beta</div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingDown className="text-purple-400" size={24} />
              <span className="text-gray-400 text-sm">TTM</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{analysis.fundamentals.pe}</div>
            <div className="text-gray-400 text-sm">P/E Ratio</div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          {/* Chart */}
          <div className="lg:col-span-2">
            <StockChart ticker={analysis.ticker} />
          </div>

          {/* Technical Indicators */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Technical Indicators</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">RSI (14)</span>
                <span className="text-white font-medium">{analysis.technicalIndicators.rsi}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">MACD</span>
                <span className="text-white font-medium">{analysis.technicalIndicators.macd}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">SMA (20)</span>
                <span className="text-white font-medium">${analysis.technicalIndicators.sma20}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">SMA (50)</span>
                <span className="text-white font-medium">${analysis.technicalIndicators.sma50}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Volume</span>
                <span className="text-white font-medium">{(analysis.technicalIndicators.volume / 1000000).toFixed(1)}M</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Fundamentals */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">Fundamentals</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white mb-1">{analysis.fundamentals.marketCap}</div>
                <div className="text-gray-400 text-sm">Market Cap</div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white mb-1">${analysis.fundamentals.eps}</div>
                <div className="text-gray-400 text-sm">EPS</div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white mb-1">{analysis.fundamentals.pe}</div>
                <div className="text-gray-400 text-sm">P/E Ratio</div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white mb-1">{analysis.fundamentals.dividend}%</div>
                <div className="text-gray-400 text-sm">Dividend Yield</div>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-6">AI Recommendations</h3>
            <div className="space-y-3">
              {analysis.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-gray-300 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent News */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Recent News & Analysis</h3>
          <div className="space-y-4">
            {analysis.news.map((item, index) => (
              <div key={index} className="border-b border-white/10 pb-4 last:border-b-0">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-medium">{item.title}</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm ${getSentimentColor(item.sentiment)}`}>
                      {item.sentiment}
                    </span>
                    <span className="text-gray-400 text-sm">{item.timestamp}</span>
                  </div>
                </div>
                <p className="text-gray-300 text-sm">{item.summary}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
