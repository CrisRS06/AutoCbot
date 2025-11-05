'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils'
import { marketApi } from '@/services/api'
import { useWebSocket } from '@/hooks/useWebSocket'
import type { MarketPrice } from '@/types'
import toast from 'react-hot-toast'

const DEFAULT_PAIRS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']

export default function LivePrices() {
  const [prices, setPrices] = useState<MarketPrice[]>([])
  const { lastMessage } = useWebSocket(['prices'])

  useEffect(() => {
    loadPrices()
    const interval = setInterval(loadPrices, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'price_update') {
      updatePrice(lastMessage.symbol, lastMessage.price, lastMessage.change_24h)
    }
  }, [lastMessage])

  const loadPrices = async () => {
    try {
      const response = await marketApi.getPrices(DEFAULT_PAIRS.join(','))
      setPrices(response.data)
    } catch (error) {
      console.error('Failed to load prices:', error)
      // BUG-005 FIX: Show user-facing error message (only once, not on every retry)
      if (prices.length === 0) {
        toast.error('Failed to load live prices. Retrying...')
      }
    }
  }

  const updatePrice = (symbol: string, price: number, change: number) => {
    setPrices(prev =>
      prev.map(p => (p.symbol === symbol ? { ...p, price, change_24h: change } : p))
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Live Prices</span>
          <span className="text-xs font-normal text-muted-foreground">Auto-updating</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {prices.map((price, index) => (
            <motion.div
              key={price.symbol}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="p-4 rounded-lg bg-accent hover:bg-accent/80 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-muted-foreground">
                  {price.symbol.split('/')[0]}
                </span>
                {price.change_24h >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
              </div>
              <p className="text-lg font-bold mb-1">
                {formatCurrency(price.price, price.price < 1 ? 4 : 2)}
              </p>
              <p className={`text-sm font-medium ${getChangeColor(price.change_24h)}`}>
                {formatPercent(price.change_24h)}
              </p>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
