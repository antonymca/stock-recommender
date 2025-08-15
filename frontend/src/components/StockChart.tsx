'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { useState, useEffect } from 'react'

interface ChartData {
  date: string
  price: number
  volume: number
}

interface StockChartProps {
  ticker: string
  timeframe?: '1D' | '1W' | '1M' | '3M' | '1Y'
}

export default function StockChart({ ticker, timeframe = '1M' }: StockChartProps) {
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe)

  useEffect(() => {
    fetchChartData()
  }, [ticker, selectedTimeframe])

  const fetchChartData = async () => {
    setLoading(true)
    try {
      // Mock chart data - replace with real API
      const mockData: ChartData[] = Array.from({ length: 30 }, (_, i) => {
        const date = new Date()
        date.setDate(date.getDate() - (29 - i))
        const basePrice = 150 + Math.random() * 50
        const volatility = Math.sin(i * 0.2) * 10 + Math.random() * 5
        
        return {
          date: date.toISOString().split('T')[0],
          price: basePrice + volatility,
          volume: Math.floor(Math.random() * 1000000) + 500000
        }
      })
      
      setData(mockData)
    } catch (error) {
      console.error('Error fetching chart data:', error)
    } finally {
      setLoading(false)
    }
  }

  const timeframes = ['1D', '1W', '1M', '3M', '1Y'] as const

  if (loading) {
    return (
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-white/10 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-white/10 rounded"></div>
        </div>
      </div>
    )
  }

  const currentPrice = data[data.length - 1]?.price || 0
  const previousPrice = data[data.length - 2]?.price || 0
  const change = currentPrice - previousPrice
  const changePercent = (change / previousPrice) * 100

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-white mb-2">{ticker} Price Chart</h3>
          <div className="flex items-center space-x-4">
            <span className="text-2xl font-bold text-white">${currentPrice.toFixed(2)}</span>
            <span className={`text-lg ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {change >= 0 ? '+' : ''}{change.toFixed(2)} ({changePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
        
        <div className="flex space-x-1">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedTimeframe === tf
                  ? 'bg-blue-500 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              fontSize={12}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis 
              stroke="#9ca3af"
              fontSize={12}
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorPrice)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}