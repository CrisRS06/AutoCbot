'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Target, Activity, Award, Calendar } from 'lucide-react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { portfolioApi } from '@/services/api'
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils'
import toast from 'react-hot-toast'

interface PerformanceMetrics {
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  profit_factor: number
  sharpe_ratio: number
  max_drawdown: number
  average_win: number
  average_loss: number
  largest_win: number
  largest_loss: number
  total_pnl: number
}

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(30)

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      const response = await portfolioApi.getPerformance()
      setMetrics(response.data)
    } catch (error) {
      console.error('Failed to load analytics:', error)
      // BUG-005 FIX: Show user-facing error message
      toast.error('Failed to load analytics data. Showing demo data.')
      // Set mock data for demo
      setMetrics({
        total_trades: 45,
        winning_trades: 28,
        losing_trades: 17,
        win_rate: 0.622,
        profit_factor: 1.85,
        sharpe_ratio: 1.42,
        max_drawdown: -0.12,
        average_win: 156.50,
        average_loss: -89.30,
        largest_win: 450.00,
        largest_loss: -220.00,
        total_pnl: 2847.50,
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6 p-6">
          <div className="animate-pulse">
            <div className="h-12 bg-muted rounded w-1/3 mb-6" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="h-32 bg-muted rounded" />
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
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
          <h1 className="text-4xl font-bold text-gradient">Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Performance metrics and insights
          </p>
        </div>
        <div className="flex gap-2">
          {[7, 30, 90, 365].map(days => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-3 py-1 rounded-lg text-sm font-medium ${
                timeRange === days
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              }`}
            >
              {days === 365 ? '1Y' : `${days}D`}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total P&L */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Total P&L</p>
              <TrendingUp className={`w-5 h-5 ${
                metrics && metrics.total_pnl >= 0 ? 'text-success' : 'text-danger'
              }`} />
            </div>
            <p className={`text-3xl font-bold ${
              metrics && getChangeColor(metrics.total_pnl)
            }`}>
              {formatCurrency(metrics?.total_pnl || 0)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Last {timeRange} days
            </p>
          </CardContent>
        </Card>

        {/* Win Rate */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <Target className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">
              {formatPercent((metrics?.win_rate || 0) * 100)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {metrics?.winning_trades || 0} wins / {metrics?.total_trades || 0} trades
            </p>
          </CardContent>
        </Card>

        {/* Profit Factor */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Profit Factor</p>
              <Activity className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">
              {metrics?.profit_factor.toFixed(2) || '0.00'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {metrics && metrics.profit_factor > 1 ? 'Profitable' : 'Unprofitable'}
            </p>
          </CardContent>
        </Card>

        {/* Sharpe Ratio */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">
              {metrics?.sharpe_ratio.toFixed(2) || '0.00'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Risk-adjusted return
            </p>
          </CardContent>
        </Card>

        {/* Max Drawdown */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Max Drawdown</p>
              <TrendingUp className="w-5 h-5 text-danger" />
            </div>
            <p className="text-3xl font-bold text-danger">
              {formatPercent((metrics?.max_drawdown || 0) * 100)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Largest peak-to-trough
            </p>
          </CardContent>
        </Card>

        {/* Total Trades */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Total Trades</p>
              <Calendar className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">{metrics?.total_trades || 0}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {((metrics?.total_trades || 0) / timeRange).toFixed(1)} per day
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Trade Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Win/Loss Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Win/Loss Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-success/5 border border-success/20 rounded-lg">
              <div>
                <p className="text-sm text-muted-foreground">Average Win</p>
                <p className="text-2xl font-bold text-success">
                  {formatCurrency(metrics?.average_win || 0)}
                </p>
              </div>
              <Award className="w-8 h-8 text-success opacity-20" />
            </div>

            <div className="flex items-center justify-between p-4 bg-danger/5 border border-danger/20 rounded-lg">
              <div>
                <p className="text-sm text-muted-foreground">Average Loss</p>
                <p className="text-2xl font-bold text-danger">
                  {formatCurrency(metrics?.average_loss || 0)}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-danger opacity-20" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 border border-border rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Largest Win</p>
                <p className="text-xl font-bold text-success">
                  {formatCurrency(metrics?.largest_win || 0)}
                </p>
              </div>
              <div className="p-4 border border-border rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Largest Loss</p>
                <p className="text-xl font-bold text-danger">
                  {formatCurrency(metrics?.largest_loss || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Trade Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Trade Distribution</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Win Rate Bar */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">Winning Trades</p>
                <p className="text-sm text-success font-semibold">
                  {metrics?.winning_trades || 0}
                </p>
              </div>
              <div className="h-4 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-success transition-all"
                  style={{ width: `${(metrics?.win_rate || 0) * 100}%` }}
                />
              </div>
            </div>

            {/* Loss Rate Bar */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">Losing Trades</p>
                <p className="text-sm text-danger font-semibold">
                  {metrics?.losing_trades || 0}
                </p>
              </div>
              <div className="h-4 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-danger transition-all"
                  style={{ width: `${((metrics?.losing_trades || 0) / (metrics?.total_trades || 1)) * 100}%` }}
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="p-4 bg-accent rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">Win Streak</p>
                <p className="text-2xl font-bold">-</p>
                <p className="text-xs text-muted-foreground">Coming soon</p>
              </div>
              <div className="p-4 bg-accent rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">Loss Streak</p>
                <p className="text-2xl font-bold">-</p>
                <p className="text-xs text-muted-foreground">Coming soon</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Profit Factor Insight */}
            {metrics && metrics.profit_factor > 1 && (
              <div className="p-4 bg-success/5 border border-success/20 rounded-lg">
                <p className="font-medium text-success mb-1">✓ Strong Profit Factor</p>
                <p className="text-sm text-muted-foreground">
                  Your profit factor of {metrics.profit_factor.toFixed(2)} indicates that your winning trades
                  are significantly larger than your losses on average.
                </p>
              </div>
            )}

            {/* Win Rate Insight */}
            {metrics && metrics.win_rate > 0.5 && (
              <div className="p-4 bg-success/5 border border-success/20 rounded-lg">
                <p className="font-medium text-success mb-1">✓ Above Average Win Rate</p>
                <p className="text-sm text-muted-foreground">
                  Your win rate of {formatPercent(metrics.win_rate * 100)} is above 50%, showing consistent
                  profitability in your trading strategy.
                </p>
              </div>
            )}

            {/* Sharpe Ratio Insight */}
            {metrics && metrics.sharpe_ratio > 1 && (
              <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
                <p className="font-medium text-primary mb-1">✓ Good Risk-Adjusted Returns</p>
                <p className="text-sm text-muted-foreground">
                  A Sharpe ratio of {metrics.sharpe_ratio.toFixed(2)} indicates good returns relative to the
                  risk taken. Keep maintaining this balance.
                </p>
              </div>
            )}

            {/* Drawdown Warning */}
            {metrics && Math.abs(metrics.max_drawdown) > 0.15 && (
              <div className="p-4 bg-warning/5 border border-warning/20 rounded-lg">
                <p className="font-medium text-warning mb-1">⚠ High Drawdown</p>
                <p className="text-sm text-muted-foreground">
                  Your maximum drawdown of {formatPercent(metrics.max_drawdown * 100)} is above 15%.
                  Consider reviewing your risk management strategy.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      </div>
    </DashboardLayout>
  )
}
