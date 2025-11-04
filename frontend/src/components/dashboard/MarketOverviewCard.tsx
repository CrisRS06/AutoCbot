'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatCurrency, formatPercent } from '@/lib/utils'
import type { MarketOverview } from '@/types'

interface Props {
  data: MarketOverview | null
  loading: boolean
}

export default function MarketOverviewCard({ data, loading }: Props) {
  if (loading) {
    return (
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle>Market Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded" />
            <div className="h-4 bg-muted rounded w-3/4" />
          </div>
        </CardContent>
      </Card>
    )
  }

  const stats = [
    {
      label: 'Total Market Cap',
      value: formatCurrency(data?.total_market_cap || 0, 0),
      icon: DollarSign,
      color: 'text-blue-500',
    },
    {
      label: 'BTC Dominance',
      value: formatPercent(data?.btc_dominance || 0),
      icon: TrendingUp,
      color: 'text-orange-500',
    },
    {
      label: '24h Volume',
      value: formatCurrency(data?.total_volume_24h || 0, 0),
      icon: Activity,
      color: 'text-purple-500',
    },
  ]

  return (
    <Card gradient hover>
      <CardHeader>
        <CardTitle className="text-lg">Market Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg bg-accent ${stat.color}`}>
                <stat.icon className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-lg font-semibold">{stat.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </CardContent>
    </Card>
  )
}
