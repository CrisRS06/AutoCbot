'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Activity, Target, Award, AlertCircle, BarChart3, DollarSign } from 'lucide-react'

interface BacktestMetrics {
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  total_return_pct: number
  net_profit: number
  sharpe_ratio: number
  sortino_ratio: number
  calmar_ratio: number
  max_drawdown: number
  max_drawdown_duration: number
  profit_factor: number
  expectancy: number
  avg_win: number
  avg_loss: number
  largest_win: number
  largest_loss: number
  recovery_factor: number
  var_95: number
  cvar_95: number
  omega_ratio: number
  tail_ratio: number
}

interface BacktestResultsProps {
  metrics: BacktestMetrics
  strategyName: string
  startDate?: string
  endDate?: string
  initialCapital?: number
}

export default function BacktestResults({
  metrics,
  strategyName,
  startDate,
  endDate,
  initialCapital = 10000
}: BacktestResultsProps) {
  const finalBalance = initialCapital + (metrics.net_profit || 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Backtest Results: {strategyName}</h2>
        {startDate && endDate && (
          <p className="text-blue-100">
            Period: {new Date(startDate).toLocaleDateString()} - {new Date(endDate).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Return */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`bg-gradient-to-br ${
            metrics.total_return_pct >= 0
              ? 'from-green-500 to-green-600'
              : 'from-red-500 to-red-600'
          } rounded-lg p-6 text-white shadow-lg`}
        >
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8" />
            <span className="text-3xl font-bold">
              {metrics.total_return_pct >= 0 ? '+' : ''}
              {(metrics.total_return_pct * 100).toFixed(2)}%
            </span>
          </div>
          <p className="text-sm opacity-90">Total Return</p>
          <p className="text-xs mt-1 opacity-75">
            ${initialCapital.toLocaleString()} → ${finalBalance.toLocaleString()}
          </p>
        </motion.div>

        {/* Win Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg"
        >
          <div className="flex items-center justify-between mb-2">
            <Target className="w-8 h-8" />
            <span className="text-3xl font-bold">
              {(metrics.win_rate * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-sm opacity-90">Win Rate</p>
          <p className="text-xs mt-1 opacity-75">
            {metrics.winning_trades}W / {metrics.losing_trades}L
          </p>
        </motion.div>

        {/* Sharpe Ratio */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg"
        >
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-8 h-8" />
            <span className="text-3xl font-bold">
              {metrics.sharpe_ratio.toFixed(2)}
            </span>
          </div>
          <p className="text-sm opacity-90">Sharpe Ratio</p>
          <p className="text-xs mt-1 opacity-75">
            Risk-Adjusted Return
          </p>
        </motion.div>

        {/* Max Drawdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-lg"
        >
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-8 h-8" />
            <span className="text-3xl font-bold">
              {(metrics.max_drawdown * 100).toFixed(2)}%
            </span>
          </div>
          <p className="text-sm opacity-90">Max Drawdown</p>
          <p className="text-xs mt-1 opacity-75">
            {metrics.max_drawdown_duration} periods
          </p>
        </motion.div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
            Performance Metrics
          </h3>
          <div className="space-y-3">
            <MetricRow label="Total Trades" value={metrics.total_trades.toString()} />
            <MetricRow
              label="Profit Factor"
              value={metrics.profit_factor.toFixed(2)}
              good={metrics.profit_factor > 1}
            />
            <MetricRow
              label="Expectancy"
              value={`$${metrics.expectancy.toFixed(2)}`}
              good={metrics.expectancy > 0}
            />
            <MetricRow label="Sortino Ratio" value={metrics.sortino_ratio.toFixed(2)} />
            <MetricRow label="Calmar Ratio" value={metrics.calmar_ratio.toFixed(2)} />
            <MetricRow label="Omega Ratio" value={metrics.omega_ratio.toFixed(2)} />
            <MetricRow label="Recovery Factor" value={metrics.recovery_factor.toFixed(2)} />
            <MetricRow label="Tail Ratio" value={metrics.tail_ratio.toFixed(2)} />
          </div>
        </div>

        {/* Trade Statistics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2 text-green-600" />
            Trade Statistics
          </h3>
          <div className="space-y-3">
            <MetricRow
              label="Average Win"
              value={`$${metrics.avg_win.toFixed(2)}`}
              good={true}
            />
            <MetricRow
              label="Average Loss"
              value={`$${metrics.avg_loss.toFixed(2)}`}
              good={false}
            />
            <MetricRow
              label="Largest Win"
              value={`$${metrics.largest_win.toFixed(2)}`}
              good={true}
            />
            <MetricRow
              label="Largest Loss"
              value={`$${metrics.largest_loss.toFixed(2)}`}
              good={false}
            />
            <MetricRow
              label="Net Profit"
              value={`$${metrics.net_profit.toFixed(2)}`}
              good={metrics.net_profit > 0}
            />
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-orange-600" />
            Risk Metrics
          </h3>
          <div className="space-y-3">
            <MetricRow
              label="Value at Risk (95%)"
              value={`${(metrics.var_95 * 100).toFixed(2)}%`}
            />
            <MetricRow
              label="Conditional VaR (95%)"
              value={`${(metrics.cvar_95 * 100).toFixed(2)}%`}
            />
            <MetricRow
              label="Max Drawdown"
              value={`${(metrics.max_drawdown * 100).toFixed(2)}%`}
              good={false}
            />
            <MetricRow
              label="Drawdown Duration"
              value={`${metrics.max_drawdown_duration} periods`}
            />
          </div>
        </div>

        {/* Rating/Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-600" />
            Strategy Rating
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Performance</span>
                <span className="text-sm font-semibold">
                  {getRating(metrics.sharpe_ratio, [0, 1, 2, 3])}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                  style={{ width: `${Math.min(metrics.sharpe_ratio * 33.33, 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Consistency</span>
                <span className="text-sm font-semibold">
                  {getRating(metrics.win_rate, [0.4, 0.5, 0.6, 0.7])}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full"
                  style={{ width: `${metrics.win_rate * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Risk Management</span>
                <span className="text-sm font-semibold">
                  {getRating(Math.abs(metrics.max_drawdown), [0.3, 0.2, 0.1, 0.05], true)}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-orange-500 to-red-600 h-2 rounded-full"
                  style={{ width: `${Math.abs(metrics.max_drawdown) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper component for metric rows
function MetricRow({
  label,
  value,
  good
}: {
  label: string
  value: string
  good?: boolean
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <span className={`text-sm font-semibold ${
        good === true ? 'text-green-600 dark:text-green-400' :
        good === false ? 'text-red-600 dark:text-red-400' :
        'text-gray-900 dark:text-gray-100'
      }`}>
        {value}
      </span>
    </div>
  )
}

// Helper function to get rating label
function getRating(value: number, thresholds: number[], inverse = false): string {
  const ratings = ['Poor', 'Fair', 'Good', 'Excellent']

  if (inverse) {
    // For metrics where lower is better (like drawdown)
    if (value > thresholds[0]) return ratings[0]
    if (value > thresholds[1]) return ratings[1]
    if (value > thresholds[2]) return ratings[2]
    return ratings[3]
  } else {
    // For metrics where higher is better
    if (value < thresholds[0]) return ratings[0]
    if (value < thresholds[1]) return ratings[1]
    if (value < thresholds[2]) return ratings[2]
    return ratings[3]
  }
}
