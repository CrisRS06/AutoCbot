'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Plus, Play, Pause, Trash2, BarChart3, TrendingUp } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { strategyApi } from '@/services/api'
import type { StrategyConfig } from '@/types'
import toast from 'react-hot-toast'

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<StrategyConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // BUG-003 FIX: Loading state for long-running backtest operations
  const [backtestingStrategy, setBacktestingStrategy] = useState<string | null>(null)
  const [backtestProgress, setBacktestProgress] = useState<string>('')

  useEffect(() => {
    loadStrategies()
  }, [])

  // BUG-004 FIX: ESC key closes modals
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // Don't close backtest modal (it's a long-running operation)
        // But DO close create modal
        if (showCreateModal) {
          setShowCreateModal(false)
        }
      }
    }

    document.addEventListener('keydown', handleEscKey)
    return () => document.removeEventListener('keydown', handleEscKey)
  }, [showCreateModal])

  const loadStrategies = async () => {
    try {
      const response = await strategyApi.list()
      setStrategies(response.data)
    } catch (error) {
      console.error('Failed to load strategies:', error)
      toast.error('Failed to load strategies')
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (name: string) => {
    try {
      await strategyApi.toggle(name)
      toast.success('Strategy updated')
      loadStrategies()
    } catch (error) {
      toast.error('Failed to toggle strategy')
    }
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete strategy "${name}"?`)) return

    try {
      await strategyApi.delete(name)
      toast.success('Strategy deleted')
      loadStrategies()
    } catch (error) {
      toast.error('Failed to delete strategy')
    }
  }

  const handleBacktest = async (name: string) => {
    setBacktestingStrategy(name)
    setBacktestProgress('Initializing backtest...')

    try {
      // Simulate progress updates for better UX
      const progressInterval = setInterval(() => {
        setBacktestProgress(prev => {
          const messages = [
            'Loading historical data...',
            'Analyzing price patterns...',
            'Running strategy signals...',
            'Calculating performance metrics...',
            'Finalizing results...',
          ]
          const currentIndex = messages.indexOf(prev)
          return messages[(currentIndex + 1) % messages.length]
        })
      }, 5000)

      const response = await strategyApi.runBacktest({
        strategy_name: name,
        pairs: ['BTC/USDT'],
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date().toISOString(),
      })

      clearInterval(progressInterval)
      toast.success('Backtest completed!')
      // TODO: Show backtest results
    } catch (error) {
      toast.error('Backtest failed')
    } finally {
      setBacktestingStrategy(null)
      setBacktestProgress('')
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-gradient">Strategies</h1>
          <p className="text-muted-foreground mt-1">
            Manage and test your trading strategies
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          Create Strategy
        </button>
      </motion.div>

      {/* Strategies Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-4">
                  <div className="h-6 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                  <div className="h-20 bg-muted rounded"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : strategies.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Strategies Yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first trading strategy to get started
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
            >
              Create Strategy
            </button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy) => (
            <motion.div
              key={strategy.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        {strategy.name}
                      </CardTitle>
                      <p className="text-xs text-muted-foreground mt-1">
                        {strategy.timeframe} • {strategy.pairs?.length || 0} pairs
                      </p>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      strategy.enabled
                        ? 'bg-success/10 text-success'
                        : 'bg-muted text-muted-foreground'
                    }`}>
                      {strategy.enabled ? 'Active' : 'Inactive'}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Strategy Stats */}
                  <div className="grid grid-cols-2 gap-4 py-4 border-y border-border">
                    <div>
                      <p className="text-xs text-muted-foreground">Win Rate</p>
                      <p className="text-lg font-semibold text-success">
                        {strategy.performance?.win_rate
                          ? `${(strategy.performance.win_rate * 100).toFixed(1)}%`
                          : 'N/A'
                        }
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Sharpe Ratio</p>
                      <p className="text-lg font-semibold">
                        {strategy.performance?.sharpe_ratio?.toFixed(2) || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Trading Pairs */}
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Trading Pairs</p>
                    <div className="flex flex-wrap gap-1">
                      {strategy.pairs?.slice(0, 3).map(pair => (
                        <span key={pair} className="px-2 py-1 bg-muted rounded text-xs">
                          {pair}
                        </span>
                      ))}
                      {(strategy.pairs?.length || 0) > 3 && (
                        <span className="px-2 py-1 bg-muted rounded text-xs">
                          +{(strategy.pairs?.length || 0) - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={() => handleToggle(strategy.name)}
                      className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        strategy.enabled
                          ? 'bg-warning/10 text-warning hover:bg-warning/20'
                          : 'bg-success/10 text-success hover:bg-success/20'
                      }`}
                    >
                      {strategy.enabled ? (
                        <>
                          <Pause className="w-4 h-4" />
                          Pause
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" />
                          Activate
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleBacktest(strategy.name)}
                      disabled={backtestingStrategy === strategy.name}
                      className="px-3 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title={backtestingStrategy === strategy.name ? 'Running backtest...' : 'Run Backtest'}
                    >
                      {backtestingStrategy === strategy.name ? (
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <BarChart3 className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(strategy.name)}
                      className="px-3 py-2 bg-danger/10 text-danger rounded-lg hover:bg-danger/20 transition-colors"
                      title="Delete Strategy"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Strategies</p>
                <p className="text-2xl font-bold">{strategies.length}</p>
              </div>
              <Activity className="w-8 h-8 text-primary opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold text-success">
                  {strategies.filter(s => s.enabled).length}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-success opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Win Rate</p>
                <p className="text-2xl font-bold">
                  {strategies.length > 0
                    ? `${(strategies.reduce((acc, s) => acc + (s.performance?.win_rate || 0), 0) / strategies.length * 100).toFixed(1)}%`
                    : 'N/A'
                  }
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-primary opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pairs Covered</p>
                <p className="text-2xl font-bold">
                  {new Set(strategies.flatMap(s => s.pairs || [])).size}
                </p>
              </div>
              <Activity className="w-8 h-8 text-primary opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Backtest Progress Modal (BUG-003 FIX) */}
      {backtestingStrategy && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-md m-4"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="w-6 h-6 border-3 border-primary border-t-transparent rounded-full animate-spin" />
                  Running Backtest
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="font-semibold mb-1">{backtestingStrategy}</p>
                  <p className="text-sm text-muted-foreground">{backtestProgress}</p>
                </div>
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                  <div className="h-full bg-primary rounded-full animate-pulse" style={{ width: '60%' }} />
                </div>
                <p className="text-xs text-muted-foreground text-center">
                  This may take 30-60 seconds. Please wait...
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      )}

      {/* Create Modal Placeholder */}
      {showCreateModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={(e) => {
            // BUG-004 FIX: Click backdrop to close modal
            if (e.target === e.currentTarget) {
              setShowCreateModal(false)
            }
          }}
        >
          <Card className="w-full max-w-2xl m-4" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <CardTitle>Create New Strategy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Strategy creation form coming soon. For now, you can create strategies via the API or configuration files.
              </p>
              <button
                onClick={() => setShowCreateModal(false)}
                className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg"
              >
                Close
              </button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
