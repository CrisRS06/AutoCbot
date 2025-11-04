'use client'

import { motion } from 'framer-motion'
import { Briefcase, X } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils'
import type { Position } from '@/types'

interface Props {
  positions: Position[]
  loading: boolean
}

export default function PositionsTable({ positions, loading }: Props) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Open Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[1, 2].map(i => (
              <div key={i} className="h-16 bg-muted rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Briefcase className="w-5 h-5" />
          Open Positions
        </CardTitle>
      </CardHeader>
      <CardContent>
        {positions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Briefcase className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No open positions</p>
          </div>
        ) : (
          <div className="space-y-3">
            {positions.map((position, index) => (
              <motion.div
                key={position.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg bg-accent hover:bg-accent/80 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-lg">{position.symbol.split('/')[0]}</p>
                    <p className="text-xs text-muted-foreground">
                      {position.amount} @ {formatCurrency(position.entry_price)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${getChangeColor(position.pnl)}`}>
                      {formatCurrency(position.pnl)}
                    </p>
                    <p className={`text-sm font-medium ${getChangeColor(position.pnl_percentage)}`}>
                      {formatPercent(position.pnl_percentage)}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <p className="text-muted-foreground">Current</p>
                    <p className="font-medium">{formatCurrency(position.current_price)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Value</p>
                    <p className="font-medium">{formatCurrency(position.value_usd)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Side</p>
                    <p className={`font-medium ${position.side === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                      {position.side.toUpperCase()}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
