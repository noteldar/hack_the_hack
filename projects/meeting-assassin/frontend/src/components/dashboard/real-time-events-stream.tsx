'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain,
  Calendar,
  Target,
  Zap,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Activity
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

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

interface RealTimeEventsStreamProps {
  events: RealTimeEvent[]
}

const eventIcons = {
  decision: Brain,
  optimization: Target,
  analysis: TrendingUp,
  intervention: Zap
}

const eventColors = {
  decision: 'from-purple-500 to-pink-500',
  optimization: 'from-blue-500 to-cyan-500',
  analysis: 'from-green-500 to-emerald-500',
  intervention: 'from-orange-500 to-red-500'
}

const impactColors = {
  high: 'bg-red-500',
  medium: 'bg-yellow-500',
  low: 'bg-blue-500'
}

export function RealTimeEventsStream({ events }: RealTimeEventsStreamProps) {
  const [visibleEvents, setVisibleEvents] = useState<RealTimeEvent[]>([])

  useEffect(() => {
    // Animate in new events one by one
    const sortedEvents = events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())

    if (sortedEvents.length !== visibleEvents.length) {
      const timer = setTimeout(() => {
        setVisibleEvents(sortedEvents)
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [events, visibleEvents.length])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getTimeAgo = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSeconds = Math.floor(diffMs / 1000)
    const diffMinutes = Math.floor(diffSeconds / 60)
    const diffHours = Math.floor(diffMinutes / 60)

    if (diffSeconds < 60) return `${diffSeconds}s ago`
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    return `${diffHours}h ago`
  }

  return (
    <Card className="glass-card h-full flex flex-col">
      <CardHeader className="pb-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            >
              <Activity className="w-5 h-5 text-orange-500" />
            </motion.div>
            <span>AI Decision Stream</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <Badge variant="outline" className="text-xs">
              {events.length} Events
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-[400px] px-6">
          <AnimatePresence initial={false}>
            {visibleEvents.map((event, index) => {
              const Icon = eventIcons[event.type]
              const colorGradient = eventColors[event.type]
              const impactColor = impactColors[event.impact]

              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20, scale: 0.9 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: 20, scale: 0.9 }}
                  transition={{
                    delay: index * 0.1,
                    type: "spring",
                    stiffness: 300,
                    damping: 20
                  }}
                  className="mb-4 last:mb-0"
                >
                  <div className="flex space-x-3 p-4 rounded-xl bg-gradient-to-r from-gray-50/50 to-white/50 dark:from-gray-800/50 dark:to-gray-900/50 border border-gray-200/50 dark:border-gray-700/50 hover:shadow-lg transition-all duration-200">
                    {/* Icon */}
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-r ${colorGradient} flex items-center justify-center flex-shrink-0 relative`}>
                      <Icon className="w-5 h-5 text-white" />
                      <motion.div
                        className="absolute inset-0 rounded-xl bg-white/20"
                        animate={{ opacity: [0, 0.3, 0] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                      />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-sm leading-tight">
                          {event.title}
                        </h4>
                        <div className={`w-2 h-2 rounded-full ${impactColor} flex-shrink-0 ml-2 mt-1`} />
                      </div>

                      <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
                        {event.description}
                      </p>

                      {/* Time saved indicator */}
                      {event.timeSaved && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="inline-flex items-center space-x-1 px-2 py-1 bg-green-100 dark:bg-green-900/20 rounded-md mb-2"
                        >
                          <Clock className="w-3 h-3 text-green-600 dark:text-green-400" />
                          <span className="text-xs font-medium text-green-600 dark:text-green-400">
                            +{event.timeSaved}h saved
                          </span>
                        </motion.div>
                      )}

                      {/* Metadata */}
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground font-medium">
                          {formatTime(event.timestamp)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <Badge
                            variant={event.impact === 'high' ? 'destructive' :
                                   event.impact === 'medium' ? 'default' : 'secondary'}
                            className="text-xs"
                          >
                            {event.impact}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {getTimeAgo(event.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>

          {visibleEvents.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-purple-500/10 to-blue-500/10 flex items-center justify-center">
                <Activity className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-2">Waiting for AI Activity</h3>
              <p className="text-sm text-muted-foreground">
                AI decisions and optimizations will appear here in real-time
              </p>
            </motion.div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}