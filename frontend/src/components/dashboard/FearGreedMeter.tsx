'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import type { FearGreedIndex } from '@/types'

interface Props {
  data: FearGreedIndex | null
  loading: boolean
}

export default function FearGreedMeter({ data, loading }: Props) {
  const value = data?.value || 50
  const classification = data?.value_classification || 'Neutral'

  const getColor = (val: number) => {
    if (val <= 24) return 'from-red-500 to-orange-500'
    if (val <= 49) return 'from-orange-500 to-yellow-500'
    if (val === 50) return 'from-yellow-500 to-yellow-500'
    if (val <= 75) return 'from-yellow-500 to-green-500'
    return 'from-green-500 to-emerald-500'
  }

  const getTextColor = (val: number) => {
    if (val <= 24) return 'text-red-500'
    if (val <= 49) return 'text-orange-500'
    if (val === 50) return 'text-yellow-500'
    if (val <= 75) return 'text-green-500'
    return 'text-emerald-500'
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Fear & Greed Index</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-muted rounded-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card gradient hover>
      <CardHeader>
        <CardTitle className="text-lg">Fear & Greed Index</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-4">
          {/* Circular Meter */}
          <div className="relative w-40 h-40">
            <svg className="w-full h-full -rotate-90">
              {/* Background circle */}
              <circle
                cx="80"
                cy="80"
                r="70"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                className="text-muted opacity-20"
              />
              {/* Progress circle */}
              <motion.circle
                cx="80"
                cy="80"
                r="70"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 70}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 70 }}
                animate={{
                  strokeDashoffset: 2 * Math.PI * 70 * (1 - value / 100),
                }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" className={getColor(value).split(' ')[0].replace('from-', 'stop-')} />
                  <stop offset="100%" className={getColor(value).split(' ')[1].replace('to-', 'stop-')} />
                </linearGradient>
              </defs>
            </svg>

            {/* Center text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <motion.span
                className={`text-4xl font-bold ${getTextColor(value)}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: 'spring' }}
              >
                {value}
              </motion.span>
              <span className="text-sm text-muted-foreground">/ 100</span>
            </div>
          </div>

          {/* Classification */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mt-6 text-center"
          >
            <p className={`text-xl font-semibold ${getTextColor(value)}`}>
              {classification}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Market Sentiment
            </p>
          </motion.div>
        </div>
      </CardContent>
    </Card>
  )
}
