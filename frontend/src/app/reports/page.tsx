'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { Download, FileText, Calendar, TrendingUp, BarChart3, PieChart } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

interface Report {
  id: string
  title: string
  type: 'portfolio' | 'market' | 'performance' | 'risk'
  description: string
  generatedAt: string
  size: string
  status: 'ready' | 'generating' | 'failed'
}

export default function ReportsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [generatingReport, setGeneratingReport] = useState<string | null>(null)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
      return
    }
    if (session) {
      fetchReports()
    }
  }, [session, status])

  const fetchReports = async () => {
    try {
      const mockReports: Report[] = [
        {
          id: '1',
          title: 'Monthly Portfolio Performance',
          type: 'portfolio',
          description: 'Comprehensive analysis of your portfolio performance for December 2023',
          generatedAt: '2023-12-15T10:30:00Z',
          size: '2.3 MB',
          status: 'ready'
        },
        {
          id: '2',
          title: 'Market Analysis Report',
          type: 'market',
          description: 'Weekly market trends and sector analysis with AI insights',
          generatedAt: '2023-12-14T15:45:00Z',
          size: '1.8 MB',
          status: 'ready'
        },
        {
          id: '3',
          title: 'Risk Assessment Report',
          type: 'risk',
          description: 'Portfolio risk analysis and diversification recommendations',
          generatedAt: '2023-12-13T09:15:00Z',
          size: '1.2 MB',
          status: 'ready'
        },
        {
          id: '4',
          title: 'Performance Analytics',
          type: 'performance',
          description: 'Detailed performance metrics and benchmark comparisons',
          generatedAt: '2023-12-12T14:20:00Z',
          size: '3.1 MB',
          status: 'ready'
        }
      ]
      
      setReports(mockReports)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching reports:', error)
      setLoading(false)
    }
  }

  const generateReport = async (type: string) => {
    setGeneratingReport(type)
    try {
      // Mock report generation
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      const newReport: Report = {
        id: Date.now().toString(),
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Report`,
        type: type as any,
        description: `Generated ${type} report with latest data`,
        generatedAt: new Date().toISOString(),
        size: `${(Math.random() * 3 + 1).toFixed(1)} MB`,
        status: 'ready'
      }
      
      setReports(prev => [newReport, ...prev])
      toast.success('Report generated successfully!')
    } catch (error) {
      console.error('Error generating report:', error)
      toast.error('Failed to generate report')
    } finally {
      setGeneratingReport(null)
    }
  }

  const downloadReport = (report: Report) => {
    // Mock download
    toast.success(`Downloading ${report.title}...`)
  }

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'portfolio': return PieChart
      case 'market': return TrendingUp
      case 'performance': return BarChart3
      case 'risk': return FileText
      default: return FileText
    }
  }

  const getReportColor = (type: string) => {
    switch (type) {
      case 'portfolio': return 'from-blue-500 to-cyan-500'
      case 'market': return 'from-green-500 to-emerald-500'
      case 'performance': return 'from-purple-500 to-indigo-500'
      case 'risk': return 'from-red-500 to-pink-500'
      default: return 'from-gray-500 to-slate-500'
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

  const reportTypes = [
    { type: 'portfolio', label: 'Portfolio Report', description: 'Comprehensive portfolio analysis' },
    { type: 'market', label: 'Market Report', description: 'Market trends and insights' },
    { type: 'performance', label: 'Performance Report', description: 'Performance metrics and analytics' },
    { type: 'risk', label: 'Risk Report', description: 'Risk assessment and recommendations' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Reports & Analytics</h1>
          <p className="text-gray-400">Generate and download comprehensive investment reports</p>
        </div>

        {/* Generate New Report */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-6">Generate New Report</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {reportTypes.map((reportType) => {
              const IconComponent = getReportIcon(reportType.type)
              const isGenerating = generatingReport === reportType.type
              
              return (
                <button
                  key={reportType.type}
                  onClick={() => generateReport(reportType.type)}
                  disabled={isGenerating}
                  className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className={`w-12 h-12 bg-gradient-to-r ${getReportColor(reportType.type)} rounded-lg flex items-center justify-center mb-4 mx-auto`}>
                    {isGenerating ? (
                      <div className="animate-spin w-6 h-6 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <IconComponent className="text-white" size={24} />
                    )}
                  </div>
                  <h3 className="font-medium text-white mb-2">{reportType.label}</h3>
                  <p className="text-gray-400 text-sm">{reportType.description}</p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Reports List */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10">
            <h2 className="text-xl font-semibold text-white">Generated Reports</h2>
          </div>
          
          <div className="divide-y divide-white/10">
            {reports.map((report) => {
              const IconComponent = getReportIcon(report.type)
              
              return (
                <div key={report.id} className="p-6 hover:bg-white/5 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 bg-gradient-to-r ${getReportColor(report.type)} rounded-lg flex items-center justify-center`}>
                        <IconComponent className="text-white" size={20} />
                      </div>
                      <div>
                        <h3 className="font-medium text-white mb-1">{report.title}</h3>
                        <p className="text-gray-400 text-sm mb-2">{report.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <Calendar size={12} />
                            <span>{format(new Date(report.generatedAt), 'MMM dd, yyyy')}</span>
                          </span>
                          <span>{report.size}</span>
                          <span className={`px-2 py-1 rounded-full ${
                            report.status === 'ready' ? 'bg-green-400/10 text-green-400' :
                            report.status === 'generating' ? 'bg-yellow-400/10 text-yellow-400' :
                            'bg-red-400/10 text-red-400'
                          }`}>
                            {report.status}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {report.status === 'ready' && (
                      <button
                        onClick={() => downloadReport(report)}
                        className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all flex items-center space-x-2"
                      >
                        <Download size={16} />
                        <span>Download</span>
                      </button>
                    )}
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