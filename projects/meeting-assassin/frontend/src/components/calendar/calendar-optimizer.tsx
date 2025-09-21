'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Clock,
  Zap,
  ChevronLeft,
  ChevronRight,
  Filter,
  Settings,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Calendar as CalendarIcon
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Progress } from '@/components/ui/progress'
import { useSocket } from '@/contexts/socket-context'

interface Meeting {
  id: string
  title: string
  start: Date
  end: Date
  attendees: string[]
  category: 'meeting' | 'focus' | 'break' | 'travel'
  priority: 'low' | 'medium' | 'high'
  status: 'scheduled' | 'optimized' | 'conflict' | 'suggested'
  color: string
  originalStart?: Date
  optimizationReason?: string
  confidence?: number
}

const timeSlots = Array.from({ length: 24 }, (_, i) => i)
const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const sampleMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Team Standup',
    start: new Date(2024, 0, 15, 9, 0),
    end: new Date(2024, 0, 15, 9, 30),
    attendees: ['john@company.com', 'jane@company.com'],
    category: 'meeting',
    priority: 'medium',
    status: 'scheduled',
    color: 'bg-blue-500'
  },
  {
    id: '2',
    title: 'Deep Work - Code Review',
    start: new Date(2024, 0, 15, 10, 0),
    end: new Date(2024, 0, 15, 12, 0),
    attendees: [],
    category: 'focus',
    priority: 'high',
    status: 'optimized',
    color: 'bg-purple-500',
    originalStart: new Date(2024, 0, 15, 11, 0),
    optimizationReason: 'Protected focus time during peak productivity hours',
    confidence: 95
  },
  {
    id: '3',
    title: 'Client Call - Project Update',
    start: new Date(2024, 0, 15, 14, 0),
    end: new Date(2024, 0, 15, 15, 0),
    attendees: ['client@external.com'],
    category: 'meeting',
    priority: 'high',
    status: 'conflict',
    color: 'bg-red-500'
  },
  {
    id: '4',
    title: 'Break',
    start: new Date(2024, 0, 15, 15, 30),
    end: new Date(2024, 0, 15, 15, 45),
    attendees: [],
    category: 'break',
    priority: 'medium',
    status: 'suggested',
    color: 'bg-green-500',
    optimizationReason: 'Suggested break after intense meeting',
    confidence: 80
  }
]

export function CalendarOptimizer() {
  const { connected, requestOptimization } = useSocket()
  const [currentWeek, setCurrentWeek] = useState(0)
  const [meetings, setMeetings] = useState<Meeting[]>(sampleMeetings)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [optimizationSettings, setOptimizationSettings] = useState({
    protectFocusTime: true,
    minimizeMeetings: true,
    respectBreaks: true,
    bufferTime: true,
    workingHours: { start: '09:00', end: '17:00' }
  })

  const handleOptimize = async () => {
    setIsOptimizing(true)

    // Simulate AI optimization
    setTimeout(() => {
      setMeetings(prev => prev.map(meeting => ({
        ...meeting,
        status: meeting.status === 'conflict' ? 'optimized' : meeting.status,
        color: meeting.status === 'conflict' ? 'bg-green-500' : meeting.color
      })))
      setIsOptimizing(false)
    }, 3000)

    if (connected) {
      requestOptimization(optimizationSettings)
    }
  }

  const getOptimizationStats = () => {
    const total = meetings.length
    const optimized = meetings.filter(m => m.status === 'optimized').length
    const conflicts = meetings.filter(m => m.status === 'conflict').length
    const suggestions = meetings.filter(m => m.status === 'suggested').length

    return { total, optimized, conflicts, suggestions }
  }

  const stats = getOptimizationStats()

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            Calendar Optimizer
          </h1>
          <p className="text-muted-foreground mt-2">
            AI-powered calendar optimization for maximum productivity
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            onClick={handleOptimize}
            disabled={isOptimizing}
            className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white"
          >
            {isOptimizing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            {isOptimizing ? 'Optimizing...' : 'Optimize Calendar'}
          </Button>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            title: 'Total Events',
            value: stats.total,
            icon: CalendarIcon,
            color: 'from-blue-500 to-cyan-500'
          },
          {
            title: 'Optimized',
            value: stats.optimized,
            icon: CheckCircle2,
            color: 'from-green-500 to-emerald-500'
          },
          {
            title: 'Conflicts',
            value: stats.conflicts,
            icon: AlertTriangle,
            color: 'from-red-500 to-pink-500'
          },
          {
            title: 'Suggestions',
            value: stats.suggestions,
            icon: TrendingUp,
            color: 'from-purple-500 to-indigo-500'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glass-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>Optimization Settings</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(optimizationSettings).map(([key, value]) => {
                if (key === 'workingHours') return null

                return (
                  <div key={key} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">
                        {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {key === 'protectFocusTime' && 'Block time for deep work'}
                        {key === 'minimizeMeetings' && 'Reduce meeting overhead'}
                        {key === 'respectBreaks' && 'Maintain healthy breaks'}
                        {key === 'bufferTime' && 'Add transition time'}
                      </p>
                    </div>
                    <Switch
                      checked={value as boolean}
                      onCheckedChange={(checked) =>
                        setOptimizationSettings(prev => ({ ...prev, [key]: checked }))
                      }
                    />
                  </div>
                )
              })}

              <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/20">
                <h4 className="text-sm font-semibold mb-2">AI Confidence</h4>
                <Progress value={87} className="mb-2" />
                <p className="text-xs text-muted-foreground">
                  Based on your patterns and preferences
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Calendar View */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="lg:col-span-3"
        >
          <Card className="glass-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-green-500" />
                  <span>This Week</span>
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm font-medium px-2">
                    Jan 15-21, 2024
                  </span>
                  <Button variant="ghost" size="sm">
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Calendar Grid */}
              <div className="grid grid-cols-8 gap-px bg-gray-200 dark:bg-gray-800 rounded-lg overflow-hidden">
                {/* Time column header */}
                <div className="bg-gray-50 dark:bg-gray-900 p-2 text-xs font-medium text-center">
                  Time
                </div>
                {/* Day headers */}
                {weekDays.map(day => (
                  <div key={day} className="bg-gray-50 dark:bg-gray-900 p-2 text-xs font-medium text-center">
                    {day}
                  </div>
                ))}

                {/* Time slots */}
                {timeSlots.slice(8, 19).map(hour => (
                  <React.Fragment key={hour}>
                    {/* Time label */}
                    <div className="bg-white dark:bg-gray-950 p-2 text-xs text-muted-foreground text-center border-r">
                      {hour}:00
                    </div>
                    {/* Day slots */}
                    {weekDays.map((day, dayIndex) => (
                      <div
                        key={`${day}-${hour}`}
                        className="bg-white dark:bg-gray-950 p-1 min-h-[60px] relative"
                      >
                        {/* Render meetings */}
                        {meetings
                          .filter(meeting =>
                            meeting.start.getHours() === hour && dayIndex === 0 // Simplified for demo
                          )
                          .map(meeting => (
                            <motion.div
                              key={meeting.id}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              whileHover={{ scale: 1.05 }}
                              className={`
                                absolute inset-1 rounded p-1 text-xs text-white cursor-pointer
                                ${meeting.color}
                                ${meeting.status === 'optimized' ? 'animate-pulse-glow' : ''}
                                ${isOptimizing && meeting.status === 'conflict' ? 'animate-pulse' : ''}
                              `}
                              onClick={() => {
                                // Handle meeting click
                              }}
                            >
                              <div className="font-medium truncate">{meeting.title}</div>
                              <div className="text-xs opacity-90">
                                {meeting.start.toLocaleTimeString('en-US', {
                                  hour: 'numeric',
                                  minute: '2-digit'
                                })}
                              </div>
                              {meeting.status === 'optimized' && (
                                <Badge className="absolute -top-1 -right-1 bg-green-500 text-white text-xs px-1">
                                  ✓
                                </Badge>
                              )}
                              {meeting.status === 'conflict' && (
                                <Badge className="absolute -top-1 -right-1 bg-red-500 text-white text-xs px-1">
                                  !
                                </Badge>
                              )}
                            </motion.div>
                          ))}
                      </div>
                    ))}
                  </React.Fragment>
                ))}
              </div>

              {/* Legend */}
              <div className="flex items-center space-x-4 mt-4 text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-blue-500 rounded"></div>
                  <span>Meeting</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-purple-500 rounded"></div>
                  <span>Focus</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span>Break</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-red-500 rounded animate-pulse"></div>
                  <span>Conflict</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Optimization Results */}
      <AnimatePresence>
        {isOptimizing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="glass-card bg-gradient-to-r from-purple-500/5 to-blue-500/5">
              <CardContent className="p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <RefreshCw className="w-5 h-5 animate-spin text-purple-500" />
                  <h3 className="text-lg font-semibold">AI is optimizing your calendar...</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Analyzing conflicts</span>
                    <span>100%</span>
                  </div>
                  <Progress value={100} />
                  <div className="flex justify-between text-sm">
                    <span>Optimizing schedules</span>
                    <span>75%</span>
                  </div>
                  <Progress value={75} />
                  <div className="flex justify-between text-sm">
                    <span>Generating suggestions</span>
                    <span>45%</span>
                  </div>
                  <Progress value={45} />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}