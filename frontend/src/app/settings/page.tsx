'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { User, Bell, Shield, Palette, Database, Mail } from 'lucide-react'
import toast from 'react-hot-toast'

interface UserSettings {
  notifications: {
    email: boolean
    push: boolean
    priceAlerts: boolean
    marketNews: boolean
  }
  preferences: {
    theme: 'dark' | 'light'
    currency: string
    timezone: string
    riskTolerance: 'conservative' | 'moderate' | 'aggressive'
  }
  privacy: {
    profileVisible: boolean
    shareAnalytics: boolean
    dataRetention: string
  }
}

export default function SettingsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      email: true,
      push: false,
      priceAlerts: true,
      marketNews: true
    },
    preferences: {
      theme: 'dark',
      currency: 'USD',
      timezone: 'America/New_York',
      riskTolerance: 'moderate'
    },
    privacy: {
      profileVisible: false,
      shareAnalytics: true,
      dataRetention: '2years'
    }
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/')
      return
    }
    if (session) {
      fetchSettings()
    }
  }, [session, status])

  const fetchSettings = async () => {
    try {
      // Mock settings fetch
      setLoading(false)
    } catch (error) {
      console.error('Error fetching settings:', error)
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      // Mock save
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved successfully!')
    } catch (error) {
      console.error('Error saving settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (section: keyof UserSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Navbar />
      
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account preferences and privacy settings</p>
        </div>

        <div className="space-y-8">
          {/* Profile Settings */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <User className="text-blue-400" size={24} />
              <h2 className="text-xl font-semibold text-white">Profile</h2>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={session.user?.name || ''}
                  disabled
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                <input
                  type="email"
                  value={session.user?.email || ''}
                  disabled
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Bell className="text-green-400" size={24} />
              <h2 className="text-xl font-semibold text-white">Notifications</h2>
            </div>
            
            <div className="space-y-4">
              {Object.entries(settings.notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <div>
                    <div className="text-white font-medium">
                      {key === 'email' && 'Email Notifications'}
                      {key === 'push' && 'Push Notifications'}
                      {key === 'priceAlerts' && 'Price Alerts'}
                      {key === 'marketNews' && 'Market News'}
                    </div>
                    <div className="text-gray-400 text-sm">
                      {key === 'email' && 'Receive notifications via email'}
                      {key === 'push' && 'Receive push notifications in browser'}
                      {key === 'priceAlerts' && 'Get notified when price targets are hit'}
                      {key === 'marketNews' && 'Receive market news and insights'}
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => updateSetting('notifications', key, e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Palette className="text-purple-400" size={24} />
              <h2 className="text-xl font-semibold text-white">Preferences</h2>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Currency</label>
                <select
                  value={settings.preferences.currency}
                  onChange={(e) => updateSetting('preferences', 'currency', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="JPY">JPY - Japanese Yen</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Risk Tolerance</label>
                <select
                  value={settings.preferences.riskTolerance}
                  onChange={(e) => updateSetting('preferences', 'riskTolerance', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="conservative">Conservative</option>
                  <option value="moderate">Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Timezone</label>
                <select
                  value={settings.preferences.timezone}
                  onChange={(e) => updateSetting('preferences', 'timezone', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                </select>
              </div>
            </div>
          </div>

          {/* Privacy Settings */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="text-red-400" size={24} />
              <h2 className="text-xl font-semibold text-white">Privacy & Security</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Share Analytics</div>
                  <div className="text-gray-400 text-sm">Help improve our service by sharing anonymous usage data</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.privacy.shareAnalytics}
                    onChange={(e) => updateSetting('privacy', 'shareAnalytics', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Data Retention</label>
                <select
                  value={settings.privacy.dataRetention}
                  onChange={(e) => updateSetting('privacy', 'dataRetention', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="1year">1 Year</option>
                  <option value="2years">2 Years</option>
                  <option value="5years">5 Years</option>
                  <option value="forever">Forever</option>
                </select>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={saveSettings}
              disabled={saving}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}