"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { socketService, startMockSocketEvents } from '@/lib/socket'

interface SocketContextType {
  isConnected: boolean
  emit: (event: string, data: any) => void
}

const SocketContext = createContext<SocketContextType | undefined>(undefined)

export function SocketProvider({ children }: { children: ReactNode }) {
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // For demo purposes, start mock events instead of real socket connection
    startMockSocketEvents()
    setIsConnected(true) // Simulate connection

    // In a real app, you would:
    // const socket = socketService.connect()
    // socket.on('connect', () => setIsConnected(true))
    // socket.on('disconnect', () => setIsConnected(false))

    return () => {
      socketService.disconnect()
      setIsConnected(false)
    }
  }, [])

  const emit = (event: string, data: any) => {
    socketService.emit(event, data)
  }

  return (
    <SocketContext.Provider value={{ isConnected, emit }}>
      {children}
    </SocketContext.Provider>
  )
}

export function useSocket() {
  const context = useContext(SocketContext)
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

// Custom hook for listening to specific socket events
export function useSocketEvent<T = any>(eventName: string, callback: (data: T) => void) {
  useEffect(() => {
    // For demo purposes, listen to custom events instead of socket events
    const handleEvent = (event: CustomEvent) => {
      if (event.detail.type === eventName) {
        callback(event.detail.data)
      }
    }

    window.addEventListener('socket-event', handleEvent as EventListener)

    return () => {
      window.removeEventListener('socket-event', handleEvent as EventListener)
    }
  }, [eventName, callback])
}

// Real-time data hook
export function useRealtimeData<T>(eventName: string, initialData: T) {
  const [data, setData] = useState<T>(initialData)

  useSocketEvent(eventName, (newData: T) => {
    setData(newData)
  })

  return data
}