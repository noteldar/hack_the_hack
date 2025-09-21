'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import socketClient, { AIStatus, CalendarUpdate, MeetingAnalysis, ProductivityMetrics, OptimizationResult } from '@/lib/socket'

interface SocketContextType {
  connected: boolean
  aiStatus: AIStatus | null
  recentCalendarUpdates: CalendarUpdate[]
  recentAnalyses: MeetingAnalysis[]
  productivityMetrics: ProductivityMetrics | null
  optimizationResults: OptimizationResult[]
  demoMode: boolean
  timeSaved: number
  realTimeEvents: RealTimeEvent[]
  avatarPersonality: 'professional' | 'friendly' | 'direct' | 'analytical'
  requestOptimization: (preferences: { [key: string]: boolean | { start: string; end: string } }) => void
  requestAnalysis: (meetingId: string) => void
  toggleDemoMode: () => void
  setAvatarPersonality: (personality: 'professional' | 'friendly' | 'direct' | 'analytical') => void
}

interface RealTimeEvent {
  id: string
  type: 'decision' | 'optimization' | 'analysis' | 'intervention'
  title: string
  description: string
  timestamp: Date
  impact: 'high' | 'medium' | 'low'
  timeSaved?: number
  data?: unknown
}

const SocketContext = createContext<SocketContextType | undefined>(undefined)

export function useSocket() {
  const context = useContext(SocketContext)
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

interface SocketProviderProps {
  children: ReactNode
}

export function SocketProvider({ children }: SocketProviderProps) {
  const [connected, setConnected] = useState(false)
  const [aiStatus, setAIStatus] = useState<AIStatus | null>(null)
  const [recentCalendarUpdates, setRecentCalendarUpdates] = useState<CalendarUpdate[]>([])
  const [recentAnalyses, setRecentAnalyses] = useState<MeetingAnalysis[]>([])
  const [productivityMetrics, setProductivityMetrics] = useState<ProductivityMetrics | null>(null)
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResult[]>([])
  const [demoMode, setDemoMode] = useState(true) // Start in demo mode for hackathon
  const [timeSaved, setTimeSaved] = useState(0)
  const [realTimeEvents, setRealTimeEvents] = useState<RealTimeEvent[]>([])
  const [avatarPersonality, setAvatarPersonalityState] = useState<'professional' | 'friendly' | 'direct' | 'analytical'>('professional')

  useEffect(() => {
    // Initialize socket connection
    const socket = socketClient.connect()

    // Connection status handlers
    socket.on('connect', () => setConnected(true))
    socket.on('disconnect', () => setConnected(false))

    // Subscribe to real-time updates
    socketClient.subscribeToAIStatus((status) => {
      setAIStatus(status)
    })

    socketClient.subscribeToCalendarUpdates((update) => {
      setRecentCalendarUpdates(prev => [update, ...prev.slice(0, 9)]) // Keep last 10
    })

    socketClient.subscribeToMeetingAnalysis((analysis) => {
      setRecentAnalyses(prev => [analysis, ...prev.slice(0, 4)]) // Keep last 5
    })

    socketClient.subscribeToProductivityMetrics((metrics) => {
      setProductivityMetrics(metrics)
    })

    socketClient.subscribeToOptimizationResults((result) => {
      setOptimizationResults(prev => [result, ...prev.slice(0, 9)])
      setTimeSaved(prev => prev + result.improvements.timeSaved)

      // Add real-time event
      const event: RealTimeEvent = {
        id: `opt-${Date.now()}`,
        type: 'optimization',
        title: `${result.type} optimization completed`,
        description: `Saved ${result.improvements.timeSaved}h, improved efficiency by ${result.improvements.efficiencyGain}%`,
        timestamp: new Date(),
        impact: result.improvements.timeSaved > 1 ? 'high' : result.improvements.timeSaved > 0.5 ? 'medium' : 'low',
        timeSaved: result.improvements.timeSaved,
        data: result
      }
      setRealTimeEvents(prev => [event, ...prev.slice(0, 19)])
    })

    // Cleanup on unmount
    return () => {
      socketClient.disconnect()
    }
  }, [])

  const requestOptimization = (preferences: { [key: string]: boolean | { start: string; end: string } }) => {
    socketClient.requestCalendarOptimization(preferences)
  }

  const requestAnalysis = (meetingId: string) => {
    socketClient.requestMeetingAnalysis(meetingId)
  }

  const toggleDemoMode = () => {
    setDemoMode(prev => !prev)
    if (!demoMode) {
      // Start demo simulation
      startDemoSimulation()
    }
  }

  const setAvatarPersonality = (personality: 'professional' | 'friendly' | 'direct' | 'analytical') => {
    setAvatarPersonalityState(personality)
    socketClient.setAvatarPersonality(personality)
  }

  // Demo simulation
  const startDemoSimulation = () => {
    const events = [
      {
        type: 'decision' as const,
        title: 'Meeting conflict detected',
        description: 'AI autonomously rescheduled conflicting meetings',
        impact: 'high' as const,
        timeSaved: 0.5
      },
      {
        type: 'optimization' as const,
        title: 'Calendar optimization running',
        description: 'Genetic algorithm improving schedule efficiency',
        impact: 'medium' as const,
        timeSaved: 1.2
      },
      {
        type: 'analysis' as const,
        title: 'Meeting effectiveness analyzed',
        description: 'Identified 3 improvement opportunities',
        impact: 'medium' as const,
        timeSaved: 0.3
      },
      {
        type: 'intervention' as const,
        title: 'Focus time protected',
        description: 'AI blocked meeting requests during deep work',
        impact: 'high' as const,
        timeSaved: 2.0
      }
    ]

    events.forEach((eventData, index) => {
      setTimeout(() => {
        const event: RealTimeEvent = {
          id: `demo-${Date.now()}-${index}`,
          ...eventData,
          timestamp: new Date()
        }
        setRealTimeEvents(prev => [event, ...prev.slice(0, 19)])
        setTimeSaved(prev => prev + (eventData.timeSaved || 0))
      }, index * 3000) // 3 seconds between events
    })
  }

  // Start demo simulation on mount if in demo mode
  useEffect(() => {
    if (demoMode) {
      startDemoSimulation()

      // Update time saved counter for demo
      const timeSavedInterval = setInterval(() => {
        setTimeSaved(prev => prev + 0.001) // Small incremental increase
      }, 1000)

      return () => clearInterval(timeSavedInterval)
    }
  }, [demoMode])

  const value: SocketContextType = {
    connected,
    aiStatus,
    recentCalendarUpdates,
    recentAnalyses,
    productivityMetrics,
    optimizationResults,
    demoMode,
    timeSaved,
    realTimeEvents,
    avatarPersonality,
    requestOptimization,
    requestAnalysis,
    toggleDemoMode,
    setAvatarPersonality,
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}