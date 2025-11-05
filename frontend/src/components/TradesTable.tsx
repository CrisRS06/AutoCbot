'use client'

import React, { useState, useMemo } from 'react'
import { ArrowUpRight, ArrowDownRight, Clock, DollarSign, TrendingUp, Filter } from 'lucide-react'

interface Trade {
  entry_timestamp: string
  exit_timestamp: string
  entry_price: number
  exit_price: number
  quantity: number
  side: string
  pnl: number
  pnl_pct: number
  duration_seconds: number
  exit_reason: string
}

interface TradesTableProps {
  trades: Trade[]
}

export default function TradesTable({ trades }: TradesTableProps) {
  const [filter, setFilter] = useState<'all' | 'wins' | 'losses'>('all')
  const [sortBy, setSortBy] = useState<'date' | 'pnl' | 'duration'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Filter trades
  const filteredTrades = useMemo(() => {
    let filtered = [...trades]

    if (filter === 'wins') {
      filtered = filtered.filter(t => t.pnl > 0)
    } else if (filter === 'losses') {
      filtered = filtered.filter(t => t.pnl < 0)
    }

    // Sort trades
    filtered.sort((a, b) => {
      let comparison = 0

      if (sortBy === 'date') {
        comparison = new Date(a.exit_timestamp).getTime() - new Date(b.exit_timestamp).getTime()
      } else if (sortBy === 'pnl') {
        comparison = a.pnl - b.pnl
      } else if (sortBy === 'duration') {
        comparison = a.duration_seconds - b.duration_seconds
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [trades, filter, sortBy, sortOrder])

  // Calculate stats
  const stats = useMemo(() => {
    const wins = trades.filter(t => t.pnl > 0)
    const losses = trades.filter(t => t.pnl < 0)

    return {
      total: trades.length,
      wins: wins.length,
      losses: losses.length,
      totalPnL: trades.reduce((sum, t) => sum + t.pnl, 0),
      avgWin: wins.length > 0 ? wins.reduce((sum, t) => sum + t.pnl, 0) / wins.length : 0,
      avgLoss: losses.length > 0 ? losses.reduce((sum, t) => sum + t.pnl, 0) / losses.length : 0
    }
  }, [trades])

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    if (seconds < 86400) {
      const hours = Math.floor(seconds / 3600)
      const mins = Math.floor((seconds % 3600) / 60)
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
    }
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    return hours > 0 ? `${days}d ${hours}h` : `${days}d`
  }

  if (!trades || trades.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <p className="text-center text-gray-500">No trades available</p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header with Stats and Filters */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Trade History</h3>
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center">
                <span className="text-gray-500 dark:text-gray-400 mr-2">Total:</span>
                <span className="font-semibold">{stats.total}</span>
              </div>
              <div className="flex items-center">
                <span className="text-gray-500 dark:text-gray-400 mr-2">Wins:</span>
                <span className="font-semibold text-green-600">{stats.wins}</span>
              </div>
              <div className="flex items-center">
                <span className="text-gray-500 dark:text-gray-400 mr-2">Losses:</span>
                <span className="font-semibold text-red-600">{stats.losses}</span>
              </div>
              <div className="flex items-center">
                <span className="text-gray-500 dark:text-gray-400 mr-2">Net P&L:</span>
                <span className={`font-semibold ${stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${stats.totalPnL.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('wins')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === 'wins'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Wins
            </button>
            <button
              onClick={() => setFilter('losses')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === 'losses'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Losses
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                #
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-gray-200"
                onClick={() => {
                  setSortBy('date')
                  setSortOrder(sortBy === 'date' ? (sortOrder === 'asc' ? 'desc' : 'asc') : 'desc')
                }}
              >
                Exit Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Entry / Exit
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-gray-200"
                onClick={() => {
                  setSortBy('pnl')
                  setSortOrder(sortBy === 'pnl' ? (sortOrder === 'asc' ? 'desc' : 'asc') : 'desc')
                }}
              >
                P&L {sortBy === 'pnl' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-700 dark:hover:text-gray-200"
                onClick={() => {
                  setSortBy('duration')
                  setSortOrder(sortBy === 'duration' ? (sortOrder === 'asc' ? 'desc' : 'asc') : 'desc')
                }}
              >
                Duration {sortBy === 'duration' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Exit Reason
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredTrades.map((trade, index) => (
              <tr
                key={index}
                className={`hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors ${
                  trade.pnl > 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'
                }`}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {index + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {new Date(trade.exit_timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm">
                    <div className="text-green-600 dark:text-green-400 flex items-center">
                      <ArrowUpRight className="w-3 h-3 mr-1" />
                      ${trade.entry_price.toFixed(2)}
                    </div>
                    <div className="text-red-600 dark:text-red-400 flex items-center mt-1">
                      <ArrowDownRight className="w-3 h-3 mr-1" />
                      ${trade.exit_price.toFixed(2)}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`text-sm font-semibold ${
                    trade.pnl >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </div>
                  <div className={`text-xs ${
                    trade.pnl >= 0 ? 'text-green-500 dark:text-green-300' : 'text-red-500 dark:text-red-300'
                  }`}>
                    {trade.pnl_pct >= 0 ? '+' : ''}{(trade.pnl_pct * 100).toFixed(2)}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {formatDuration(trade.duration_seconds)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    trade.exit_reason === 'take_profit'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : trade.exit_reason === 'stop_loss'
                      ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                      : trade.exit_reason === 'signal'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                  }`}>
                    {trade.exit_reason.replace('_', ' ')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredTrades.length === 0 && (
        <div className="p-6 text-center text-gray-500">
          No trades match the selected filter
        </div>
      )}
    </div>
  )
}
