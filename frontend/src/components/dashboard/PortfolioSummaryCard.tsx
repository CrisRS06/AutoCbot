'use client'

import { motion } from 'framer-motion'
import { Wallet, TrendingUp, Activity } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils'
import type { PortfolioSummary } from '@/types'

interface Props {
  data: PortfolioSummary | null
  loading: boolean
}

export default function PortfolioSummaryCard({ data, loading }: Props) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Portfolio Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-12 bg-muted rounded" />
            <div className="h-8 bg-muted rounded" />
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalValue = data?.total_value || 0
  const totalPnL = data?.total_pnl || 0
  const totalPnLPercent = data?.total_pnl_percentage || 0
  const openPositions = data?.open_positions || 0

  return (
    <Card gradient hover>
      <CardHeader>
        <CardTitle className="text-lg">Portfolio Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Total Value */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-sm text-muted-foreground mb-1">Total Value</p>
          <p className="text-3xl font-bold">{formatCurrency(totalValue)}</p>
        </motion.div>

        {/* P&L */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-between p-3 rounded-lg bg-accent"
        >
          <div className="flex items-center gap-2">
            <TrendingUp className={`w-5 h-5 ${getChangeColor(totalPnL)}`} />
            <div>
              <p className="text-xs text-muted-foreground">Total P&L</p>
              <p className={`text-lg font-semibold ${getChangeColor(totalPnL)}`}>
                {formatCurrency(totalPnL)}
              </p>
            </div>
          </div>
          <p className={`text-lg font-semibold ${getChangeColor(totalPnLPercent)}`}>
            {formatPercent(totalPnLPercent)}
          </p>
        </motion.div>

        {/* Open Positions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center gap-3"
        >
          <div className="p-2 rounded-lg bg-primary/10">
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Open Positions</p>
            <p className="text-xl font-semibold">{openPositions}</p>
          </div>
        </motion.div>
      </CardContent>
    </Card>
  )
}
