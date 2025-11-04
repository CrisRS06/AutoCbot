import { useEffect, useRef, useState } from 'react'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

export interface WebSocketMessage {
  type: string
  data?: any
  symbol?: string
  price?: number
  change_24h?: number
}

export function useWebSocket(channels: string[] = []) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(WS_URL)

        ws.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)

          // Subscribe to channels
          channels.forEach(channel => {
            ws.send(`subscribe:${channel}`)
          })
        }

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            setLastMessage(message)
          } catch (error) {
            console.error('Failed to parse message:', error)
          }
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)

          // Reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 3000)
        }

        wsRef.current = ws
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error)
        // Retry after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, 3000)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [channels.join(',')])

  return { isConnected, lastMessage }
}
