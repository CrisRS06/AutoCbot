'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, X, DollarSign, Percent, AlertTriangle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { tradingApi, marketApi } from '@/services/api'
import { formatCurrency, formatPercent } from '@/lib/utils'
import toast from 'react-hot-toast'

interface Order {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit'
  amount: number
  price?: number
  status: string
  timestamp: string
}

export default function TradingPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [showOrderForm, setShowOrderForm] = useState(false)

  // Order form state
  const [orderForm, setOrderForm] = useState({
    symbol: 'BTC/USDT',
    side: 'buy' as 'buy' | 'sell',
    type: 'market' as 'market' | 'limit',
    amount: '',
    price: '',
    stopLoss: '',
    takeProfit: '',
  })

  useEffect(() => {
    loadOrders()
  }, [])

  const loadOrders = async () => {
    try {
      const response = await tradingApi.getOrders('open')
      setOrders(response.data)
    } catch (error) {
      console.error('Failed to load orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePlaceOrder = async () => {
    try {
      const orderData = {
        symbol: orderForm.symbol,
        side: orderForm.side,
        type: orderForm.type,
        amount: parseFloat(orderForm.amount),
        price: orderForm.price ? parseFloat(orderForm.price) : undefined,
        stop_loss: orderForm.stopLoss ? parseFloat(orderForm.stopLoss) : undefined,
        take_profit: orderForm.takeProfit ? parseFloat(orderForm.takeProfit) : undefined,
      }

      await tradingApi.createOrder(orderData)
      toast.success('Order placed successfully!')
      setShowOrderForm(false)
      setOrderForm({
        symbol: 'BTC/USDT',
        side: 'buy',
        type: 'market',
        amount: '',
        price: '',
        stopLoss: '',
        takeProfit: '',
      })
      loadOrders()
    } catch (error) {
      toast.error('Failed to place order')
    }
  }

  const handleCancelOrder = async (orderId: string) => {
    try {
      await tradingApi.cancelOrder(orderId)
      toast.success('Order cancelled')
      loadOrders()
    } catch (error) {
      toast.error('Failed to cancel order')
    }
  }

  const handleCloseAll = async () => {
    if (!confirm('Are you sure you want to close ALL positions?')) return

    try {
      await tradingApi.closeAllPositions()
      toast.success('All positions closed')
      loadOrders()
    } catch (error) {
      toast.error('Failed to close positions')
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-gradient">Manual Trading</h1>
          <p className="text-muted-foreground mt-1">
            Place orders and manage your trades
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleCloseAll}
            className="px-4 py-2 bg-danger/10 text-danger rounded-lg hover:bg-danger/20"
          >
            Close All Positions
          </button>
          <button
            onClick={() => setShowOrderForm(true)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            New Order
          </button>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <TrendingUp className="w-8 h-8 mx-auto text-success mb-2" />
              <p className="text-sm font-medium mb-2">Quick Buy</p>
              <button
                onClick={() => {
                  setOrderForm({ ...orderForm, side: 'buy', type: 'market' })
                  setShowOrderForm(true)
                }}
                className="w-full px-4 py-2 bg-success text-white rounded-lg hover:bg-success/90"
              >
                Market Buy
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <TrendingDown className="w-8 h-8 mx-auto text-danger mb-2" />
              <p className="text-sm font-medium mb-2">Quick Sell</p>
              <button
                onClick={() => {
                  setOrderForm({ ...orderForm, side: 'sell', type: 'market' })
                  setShowOrderForm(true)
                }}
                className="w-full px-4 py-2 bg-danger text-white rounded-lg hover:bg-danger/90"
              >
                Market Sell
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <DollarSign className="w-8 h-8 mx-auto text-primary mb-2" />
              <p className="text-sm font-medium mb-2">Limit Order</p>
              <button
                onClick={() => {
                  setOrderForm({ ...orderForm, type: 'limit' })
                  setShowOrderForm(true)
                }}
                className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
              >
                Limit Order
              </button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Open Orders */}
      <Card>
        <CardHeader>
          <CardTitle>Open Orders</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse h-16 bg-muted rounded" />
              ))}
            </div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12">
              <TrendingUp className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No open orders</p>
              <button
                onClick={() => setShowOrderForm(true)}
                className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
              >
                Place Your First Order
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map(order => (
                <div
                  key={order.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${
                      order.side === 'buy' ? 'bg-success/10' : 'bg-danger/10'
                    }`}>
                      {order.side === 'buy' ? (
                        <TrendingUp className="w-5 h-5 text-success" />
                      ) : (
                        <TrendingDown className="w-5 h-5 text-danger" />
                      )}
                    </div>
                    <div>
                      <p className="font-semibold">{order.symbol}</p>
                      <p className="text-sm text-muted-foreground">
                        {order.type.toUpperCase()} • {order.amount} units
                        {order.price && ` @ ${formatCurrency(order.price)}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">{order.status}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(order.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    <button
                      onClick={() => handleCancelOrder(order.id)}
                      className="p-2 text-danger hover:bg-danger/10 rounded-lg"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Order Form Modal */}
      {showOrderForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-lg"
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Place Order</CardTitle>
                  <button
                    onClick={() => setShowOrderForm(false)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Symbol */}
                <div>
                  <label className="block text-sm font-medium mb-2">Trading Pair</label>
                  <select
                    value={orderForm.symbol}
                    onChange={(e) => setOrderForm({ ...orderForm, symbol: e.target.value })}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                  >
                    <option value="BTC/USDT">BTC/USDT</option>
                    <option value="ETH/USDT">ETH/USDT</option>
                    <option value="BNB/USDT">BNB/USDT</option>
                    <option value="SOL/USDT">SOL/USDT</option>
                  </select>
                </div>

                {/* Side & Type */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Side</label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => setOrderForm({ ...orderForm, side: 'buy' })}
                        className={`px-3 py-2 rounded-lg font-medium ${
                          orderForm.side === 'buy'
                            ? 'bg-success text-white'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        Buy
                      </button>
                      <button
                        onClick={() => setOrderForm({ ...orderForm, side: 'sell' })}
                        className={`px-3 py-2 rounded-lg font-medium ${
                          orderForm.side === 'sell'
                            ? 'bg-danger text-white'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        Sell
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Type</label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => setOrderForm({ ...orderForm, type: 'market' })}
                        className={`px-3 py-2 rounded-lg font-medium text-sm ${
                          orderForm.type === 'market'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        Market
                      </button>
                      <button
                        onClick={() => setOrderForm({ ...orderForm, type: 'limit' })}
                        className={`px-3 py-2 rounded-lg font-medium text-sm ${
                          orderForm.type === 'limit'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        Limit
                      </button>
                    </div>
                  </div>
                </div>

                {/* Amount */}
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input
                    type="number"
                    step="0.001"
                    value={orderForm.amount}
                    onChange={(e) => setOrderForm({ ...orderForm, amount: e.target.value })}
                    placeholder="0.00"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                  />
                </div>

                {/* Price (for limit orders) */}
                {orderForm.type === 'limit' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Price (USDT)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={orderForm.price}
                      onChange={(e) => setOrderForm({ ...orderForm, price: e.target.value })}
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                    />
                  </div>
                )}

                {/* Stop Loss & Take Profit */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Stop Loss %</label>
                    <input
                      type="number"
                      step="0.1"
                      value={orderForm.stopLoss}
                      onChange={(e) => setOrderForm({ ...orderForm, stopLoss: e.target.value })}
                      placeholder="-5.0"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Take Profit %</label>
                    <input
                      type="number"
                      step="0.1"
                      value={orderForm.takeProfit}
                      onChange={(e) => setOrderForm({ ...orderForm, takeProfit: e.target.value })}
                      placeholder="3.0"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                    />
                  </div>
                </div>

                {/* Warning */}
                <div className="p-3 bg-warning/10 border border-warning/20 rounded-lg flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-warning mt-0.5" />
                  <p className="text-sm text-muted-foreground">
                    {orderForm.type === 'market'
                      ? 'Market orders execute immediately at current market price'
                      : 'Limit orders only execute when price reaches your specified level'
                    }
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setShowOrderForm(false)}
                    className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-accent"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handlePlaceOrder}
                    disabled={!orderForm.amount}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                      orderForm.side === 'buy'
                        ? 'bg-success text-white hover:bg-success/90'
                        : 'bg-danger text-white hover:bg-danger/90'
                    } disabled:opacity-50`}
                  >
                    Place {orderForm.side.toUpperCase()} Order
                  </button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      )}
    </div>
  )
}
