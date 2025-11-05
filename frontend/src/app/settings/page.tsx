'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Save, Key, DollarSign, Shield, Bell, Database } from 'lucide-react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import toast from 'react-hot-toast'

interface Settings {
  // API Keys
  binanceApiKey: string
  binanceSecret: string
  coinGeckoApiKey: string
  telegramToken: string
  telegramChatId: string

  // Trading Parameters
  defaultPairs: string
  defaultTimeframe: string
  maxPositionSize: number
  maxOpenTrades: number

  // Risk Management
  defaultStoploss: number
  defaultTakeprofit: number

  // Features
  enableMlPredictions: boolean
  enablePaperTrading: boolean
  dryRun: boolean
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    binanceApiKey: '',
    binanceSecret: '',
    coinGeckoApiKey: '',
    telegramToken: '',
    telegramChatId: '',
    defaultPairs: 'BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT',
    defaultTimeframe: '5m',
    maxPositionSize: 0.1,
    maxOpenTrades: 5,
    defaultStoploss: -0.05,
    defaultTakeprofit: 0.03,
    enableMlPredictions: true,
    enablePaperTrading: true,
    dryRun: true,
  })

  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [saved, setSaved] = useState(false)

  // Load settings on mount
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/settings/`)
      if (!response.ok) {
        throw new Error('Failed to load settings')
      }
      const data = await response.json()
      setSettings(data)
    } catch (error) {
      console.error('Failed to load settings:', error)
      toast.error('Failed to load settings')
    } finally {
      setInitialLoading(false)
    }
  }

  const handleChange = (field: keyof Settings, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }))
    setSaved(false)
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/settings/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      })

      if (!response.ok) {
        throw new Error('Failed to save settings')
      }

      toast.success('Settings saved successfully!')
      setSaved(true)

      // Reload settings to confirm persistence
      await loadSettings()
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-bold text-gradient">Settings</h1>
            <p className="text-muted-foreground mt-1">
              Configure your trading bot parameters and API keys
            </p>
          </div>
        <button
          onClick={handleSave}
          disabled={loading || saved}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {loading ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
        </button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Keys Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5" />
              API Keys
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Binance API Key</label>
              <input
                type="password"
                value={settings.binanceApiKey}
                onChange={(e) => handleChange('binanceApiKey', e.target.value)}
                placeholder="Enter Binance API key"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Binance Secret</label>
              <input
                type="password"
                value={settings.binanceSecret}
                onChange={(e) => handleChange('binanceSecret', e.target.value)}
                placeholder="Enter Binance secret"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">CoinGecko API Key (Optional)</label>
              <input
                type="password"
                value={settings.coinGeckoApiKey}
                onChange={(e) => handleChange('coinGeckoApiKey', e.target.value)}
                placeholder="Enter CoinGecko API key"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </CardContent>
        </Card>

        {/* Trading Parameters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Trading Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Default Trading Pairs</label>
              <input
                type="text"
                value={settings.defaultPairs}
                onChange={(e) => handleChange('defaultPairs', e.target.value)}
                placeholder="BTC/USDT,ETH/USDT"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">Comma-separated list</p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Default Timeframe</label>
              <select
                value={settings.defaultTimeframe}
                onChange={(e) => handleChange('defaultTimeframe', e.target.value)}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="1m">1 minute</option>
                <option value="5m">5 minutes</option>
                <option value="15m">15 minutes</option>
                <option value="1h">1 hour</option>
                <option value="4h">4 hours</option>
                <option value="1d">1 day</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Max Position Size (% of portfolio)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.maxPositionSize}
                onChange={(e) => handleChange('maxPositionSize', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {(settings.maxPositionSize * 100).toFixed(0)}% per trade
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Max Open Trades</label>
              <input
                type="number"
                min="1"
                max="20"
                value={settings.maxOpenTrades}
                onChange={(e) => handleChange('maxOpenTrades', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </CardContent>
        </Card>

        {/* Risk Management */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Risk Management
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Default Stop Loss (%)</label>
              <input
                type="number"
                step="0.01"
                max="0"
                value={settings.defaultStoploss}
                onChange={(e) => handleChange('defaultStoploss', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {(settings.defaultStoploss * 100).toFixed(1)}% loss limit
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Default Take Profit (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={settings.defaultTakeprofit}
                onChange={(e) => handleChange('defaultTakeprofit', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {(settings.defaultTakeprofit * 100).toFixed(1)}% profit target
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Telegram Bot Token</label>
              <input
                type="password"
                value={settings.telegramToken}
                onChange={(e) => handleChange('telegramToken', e.target.value)}
                placeholder="Enter Telegram bot token"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Telegram Chat ID</label>
              <input
                type="text"
                value={settings.telegramChatId}
                onChange={(e) => handleChange('telegramChatId', e.target.value)}
                placeholder="Enter chat ID"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </CardContent>
        </Card>

        {/* Feature Flags */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Feature Flags
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div>
                  <p className="font-medium">ML Predictions</p>
                  <p className="text-xs text-muted-foreground">Use machine learning models</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableMlPredictions}
                    onChange={(e) => handleChange('enableMlPredictions', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div>
                  <p className="font-medium">Paper Trading</p>
                  <p className="text-xs text-muted-foreground">Simulate trades without real money</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enablePaperTrading}
                    onChange={(e) => handleChange('enablePaperTrading', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div>
                  <p className="font-medium">Dry Run</p>
                  <p className="text-xs text-muted-foreground">Test mode (no real orders)</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.dryRun}
                    onChange={(e) => handleChange('dryRun', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Warning Banner */}
      {!settings.dryRun && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-4 border-2 border-warning bg-warning/10 rounded-lg"
        >
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-warning mt-0.5" />
            <div>
              <p className="font-semibold text-warning">Live Trading Enabled</p>
              <p className="text-sm text-muted-foreground mt-1">
                Real money is at risk. Ensure you have tested your strategies thoroughly in paper trading mode first.
              </p>
            </div>
          </div>
        </motion.div>
      )}
      </div>
    </DashboardLayout>
  )
}
