'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Navbar from '@/components/Navbar'
import { TrendingUp, BarChart3, Shield, Zap, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (session) {
      router.push('/dashboard')
    }
  }, [session, router])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (session) {
    return null // Will redirect to dashboard
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-white mb-6">
            AI-Powered Stock
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Analysis</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Make smarter investment decisions with our advanced AI algorithms. 
            Get real-time analysis, portfolio management, and personalized recommendations.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Link
              href="/dashboard"
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center space-x-2"
            >
              <span>Get Started</span>
              <ArrowRight size={20} />
            </Link>
            <button className="border border-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition-all">
              Learn More
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          {[
            {
              icon: TrendingUp,
              title: 'Real-time Analysis',
              description: 'Get instant AI-powered stock analysis with buy/sell/hold recommendations',
              color: 'from-green-500 to-emerald-500'
            },
            {
              icon: BarChart3,
              title: 'Portfolio Management',
              description: 'Track your investments with comprehensive portfolio analytics and insights',
              color: 'from-blue-500 to-cyan-500'
            },
            {
              icon: Shield,
              title: 'Risk Assessment',
              description: 'Understand your risk exposure with detailed risk analysis and recommendations',
              color: 'from-red-500 to-pink-500'
            },
            {
              icon: Zap,
              title: 'Smart Alerts',
              description: 'Never miss opportunities with intelligent price alerts and market notifications',
              color: 'from-purple-500 to-indigo-500'
            }
          ].map((feature, index) => (
            <div key={index} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all">
              <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                <feature.icon className="text-white" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-8">Trusted by Investors Worldwide</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="text-4xl font-bold text-blue-400 mb-2">10,000+</div>
              <div className="text-gray-400">Active Users</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-400 mb-2">$50M+</div>
              <div className="text-gray-400">Assets Analyzed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-400 mb-2">95%</div>
              <div className="text-gray-400">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
