'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wallet, TrendingUp, TrendingDown, PieChart, Clock, DollarSign } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { portfolioApi } from '@/services/api'
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils'
import type { Position, PortfolioSummary } from '@/types'

export default function PortfolioPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(30)

  useEffect(() => {
    loadPortfolioData()
  }, [timeRange])

  const loadPortfolioData = async () => {
    try {
      const [summaryRes, positionsRes, historyRes] = await Promise.all([
        portfolioApi.getSummary(),
        portfolioApi.getPositions(),
        portfolioApi.getHistory(timeRange),
      ])

      setSummary(summaryRes.data)
      setPositions(positionsRes.data)
      setHistory(historyRes.data)
    } catch (error) {
      console.error('Failed to load portfolio:', error)
    } finally {
      setLoading(false)
    }
  }

  const totalPnL = summary?.pnl || 0
  const totalPnLPercent = summary?.pnl_percentage || 0

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-gradient">Portfolio</h1>
          <p className="text-muted-foreground mt-1">
            Track your holdings and performance
          </p>
        </div>
        <div className="flex gap-2">
          {[7, 30, 90].map(days => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-3 py-1 rounded-lg text-sm font-medium ${
                timeRange === days
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-accent'
              }`}
            >
              {days}D
            </button>
          ))}
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Total Value</p>
              <DollarSign className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">
              {formatCurrency(summary?.total_value || 0)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Available: {formatCurrency(summary?.available_balance || 0)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Total P&L</p>
              {totalPnL >= 0 ? (
                <TrendingUp className="w-5 h-5 text-success" />
              ) : (
                <TrendingDown className="w-5 h-5 text-danger" />
              )}
            </div>
            <p className={`text-3xl font-bold ${getChangeColor(totalPnL)}`}>
              {formatCurrency(totalPnL)}
            </p>
            <p className={`text-sm mt-1 ${getChangeColor(totalPnL)}`}>
              {formatPercent(totalPnLPercent)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Open Positions</p>
              <Wallet className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">{summary?.open_positions || 0}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {positions.length} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <PieChart className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold">
              {formatPercent(summary?.win_rate || 0)}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Last {timeRange} days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Current Positions */}
      <Card>
        <CardHeader>
          <CardTitle>Current Positions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse h-20 bg-muted rounded" />
              ))}
            </div>
          ) : positions.length === 0 ? (
            <div className="text-center py-12">
              <Wallet className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No open positions</p>
            </div>
          ) : (
            <div className="space-y-3">
              {positions.map((position) => {
                const pnl = position.pnl || 0
                const pnlPercent = position.pnl_percentage || 0

                return (
                  <div
                    key={position.id}
                    className="p-4 border border-border rounded-lg hover:border-primary/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      {/* Symbol & Side */}
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-lg ${
                          position.side === 'long' ? 'bg-success/10' : 'bg-danger/10'
                        }`}>
                          {position.side === 'long' ? (
                            <TrendingUp className="w-5 h-5 text-success" />
                          ) : (
                            <TrendingDown className="w-5 h-5 text-danger" />
                          )}
                        </div>
                        <div>
                          <p className="font-semibold text-lg">{position.symbol}</p>
                          <p className="text-sm text-muted-foreground">
                            {position.side.toUpperCase()} • {position.amount} units
                          </p>
                        </div>
                      </div>

                      {/* Prices */}
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Entry</p>
                        <p className="font-medium">{formatCurrency(position.entry_price)}</p>
                      </div>

                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Current</p>
                        <p className="font-medium">{formatCurrency(position.current_price)}</p>
                      </div>

                      {/* P&L */}
                      <div className="text-right">
                        <p className={`text-lg font-bold ${getChangeColor(pnl)}`}>
                          {formatCurrency(pnl)}
                        </p>
                        <p className={`text-sm ${getChangeColor(pnl)}`}>
                          {formatPercent(pnlPercent)}
                        </p>
                      </div>

                      {/* Stop Loss & Take Profit */}
                      <div className="text-right text-xs">
                        {position.stop_loss && (
                          <p className="text-danger">
                            SL: {formatCurrency(position.stop_loss)}
                          </p>
                        )}
                        {position.take_profit && (
                          <p className="text-success">
                            TP: {formatCurrency(position.take_profit)}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trade History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Recent Trades
          </CardTitle>
        </CardHeader>
        <CardContent>
          {history.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-muted-foreground text-sm">No trade history</p>
            </div>
          ) : (
            <div className="space-y-2">
              {history.slice(0, 10).map((trade, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 border border-border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      trade.pnl >= 0 ? 'bg-success' : 'bg-danger'
                    }`} />
                    <div>
                      <p className="font-medium">{trade.symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(trade.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${getChangeColor(trade.pnl)}`}>
                      {formatCurrency(trade.pnl)}
                    </p>
                    <p className={`text-xs ${getChangeColor(trade.pnl)}`}>
                      {formatPercent(trade.pnl_percentage)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
