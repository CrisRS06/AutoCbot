'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, Target, AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatCurrency } from '@/lib/utils'
import type { TradingSignal } from '@/types'

interface Props {
  signals: TradingSignal[]
  loading: boolean
}

export default function TradingSignals({ signals, loading }: Props) {
  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'sell':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'sell':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Trading Signals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map(i => (
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
          <Target className="w-5 h-5" />
          Trading Signals
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {signals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <p>No active signals</p>
            </div>
          ) : (
            signals.map((signal, index) => (
              <motion.div
                key={signal.symbol + signal.timestamp}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg bg-accent hover:bg-accent/80 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    {getSignalIcon(signal.signal)}
                    <div>
                      <p className="font-semibold">{signal.symbol.split('/')[0]}</p>
                      <p className="text-xs text-muted-foreground">{signal.strategy}</p>
                    </div>
                  </div>
                  <div
                    className={`px-3 py-1 rounded-full border text-xs font-medium uppercase ${getSignalColor(
                      signal.signal
                    )}`}
                  >
                    {signal.signal}
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <p className="text-muted-foreground">Entry</p>
                    <p className="font-medium">{formatCurrency(signal.entry_price, 2)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Take Profit</p>
                    <p className="font-medium text-green-500">
                      {formatCurrency(signal.take_profit, 2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Stop Loss</p>
                    <p className="font-medium text-red-500">
                      {formatCurrency(signal.stop_loss, 2)}
                    </p>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${signal.confidence * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Confidence: {(signal.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
