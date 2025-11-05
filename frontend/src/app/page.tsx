'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MarketOverviewCard from '@/components/dashboard/MarketOverviewCard'
import FearGreedMeter from '@/components/dashboard/FearGreedMeter'
import LivePrices from '@/components/dashboard/LivePrices'
import TradingSignals from '@/components/dashboard/TradingSignals'
import PortfolioSummaryCard from '@/components/dashboard/PortfolioSummaryCard'
import PositionsTable from '@/components/dashboard/PositionsTable'
import { marketApi, sentimentApi, tradingApi, portfolioApi } from '@/services/api'
import type { MarketOverview, FearGreedIndex, TradingSignal, PortfolioSummary, Position } from '@/types'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null)
  const [fearGreed, setFearGreed] = useState<FearGreedIndex | null>(null)
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null)
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const [marketRes, fearGreedRes, signalsRes, portfolioRes, positionsRes] = await Promise.all([
        marketApi.getOverview(),
        sentimentApi.getFearGreed(),
        tradingApi.getSignals('BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT'),
        portfolioApi.getSummary(),
        portfolioApi.getPositions(),
      ])

      setMarketOverview(marketRes.data)
      setFearGreed(fearGreedRes.data)
      setSignals(signalsRes.data)
      setPortfolio(portfolioRes.data)
      setPositions(positionsRes.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      // BUG-005 FIX: Show user-facing error message
      toast.error('Failed to load dashboard data. Please check your connection.')
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
            <h1 className="text-4xl font-bold text-gradient">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              AI-Powered Crypto Trading • Real-time Analytics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20">
              <span className="text-green-500 text-sm font-medium">● Live</span>
            </div>
          </div>
        </motion.div>

        {/* Top Stats Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <MarketOverviewCard data={marketOverview} loading={loading} />
          <FearGreedMeter data={fearGreed} loading={loading} />
          <PortfolioSummaryCard data={portfolio} loading={loading} />
        </div>

        {/* Live Prices */}
        <LivePrices />

        {/* Signals and Positions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TradingSignals signals={signals} loading={loading} />
          <PositionsTable positions={positions} loading={loading} />
        </div>
      </div>
    </DashboardLayout>
  )
}
