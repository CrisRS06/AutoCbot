'use client'

import React, { useMemo } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { TrendingUp } from 'lucide-react'

interface EquityPoint {
  timestamp: string
  balance: number
}

interface EquityCurveChartProps {
  equityCurve: EquityPoint[]
  initialCapital?: number
}

export default function EquityCurveChart({
  equityCurve,
  initialCapital = 10000
}: EquityCurveChartProps) {
  // Process data for chart
  const chartData = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) return []

    return equityCurve.map((point, index) => {
      const date = new Date(point.timestamp)
      const balance = point.balance

      // Calculate drawdown
      const runningMax = equityCurve
        .slice(0, index + 1)
        .reduce((max, p) => Math.max(max, p.balance), 0)

      const drawdown = ((balance - runningMax) / runningMax) * 100

      return {
        timestamp: date.toLocaleDateString(),
        fullTimestamp: date.toLocaleString(),
        balance: balance,
        drawdown: drawdown,
        profit: balance - initialCapital
      }
    })
  }, [equityCurve, initialCapital])

  // Calculate statistics
  const stats = useMemo(() => {
    if (chartData.length === 0) return null

    const finalBalance = chartData[chartData.length - 1].balance
    const maxBalance = Math.max(...chartData.map(d => d.balance))
    const minBalance = Math.min(...chartData.map(d => d.balance))
    const maxDrawdown = Math.min(...chartData.map(d => d.drawdown))

    return {
      finalBalance,
      maxBalance,
      minBalance,
      maxDrawdown,
      totalReturn: ((finalBalance - initialCapital) / initialCapital) * 100
    }
  }, [chartData, initialCapital])

  if (!chartData || chartData.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p className="text-center text-gray-500">No equity curve data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Equity Curve */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
            Equity Curve
          </h3>
          {stats && (
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Final Balance
              </p>
              <p className={`text-lg font-bold ${
                stats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${stats.finalBalance.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </p>
              <p className="text-xs text-gray-500">
                {stats.totalReturn >= 0 ? '+' : ''}
                {stats.totalReturn.toFixed(2)}%
              </p>
            </div>
          )}
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value: number, name: string) => {
                if (name === 'balance') {
                  return [`$${value.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}`, 'Balance']
                }
                return value
              }}
              labelFormatter={(label) => chartData.find(d => d.timestamp === label)?.fullTimestamp || label}
            />
            <ReferenceLine
              y={initialCapital}
              stroke="#9ca3af"
              strokeDasharray="3 3"
              label={{ value: 'Initial Capital', fill: '#9ca3af', fontSize: 12 }}
            />
            <Area
              type="monotone"
              dataKey="balance"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorBalance)"
            />
          </AreaChart>
        </ResponsiveContainer>

        {/* Stats Bar */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Peak Balance</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                ${stats.maxBalance.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Lowest Balance</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                ${stats.minBalance.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Max Drawdown</p>
              <p className="text-sm font-semibold text-red-600">
                {stats.maxDrawdown.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total Return</p>
              <p className={`text-sm font-semibold ${
                stats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.totalReturn >= 0 ? '+' : ''}
                {stats.totalReturn.toFixed(2)}%
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Drawdown Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Drawdown Analysis</h3>

        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickFormatter={(value) => `${value.toFixed(1)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, 'Drawdown']}
              labelFormatter={(label) => chartData.find(d => d.timestamp === label)?.fullTimestamp || label}
            />
            <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="drawdown"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorDrawdown)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
