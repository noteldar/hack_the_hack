'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Clock,
  TrendingUp,
  Bot,
  Target,
  Zap,
  Users,
  ChevronRight,
  Activity,
  DollarSign,
  Brain,
  Gauge,
  LineChart,
  PlayCircle,
  PauseCircle,
  RotateCcw,
  Sparkles
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useSocket } from '@/contexts/socket-context'
import { ProductivityMetricsWidget } from '@/components/dashboard/productivity-metrics-widget'
import { RealTimeEventsStream } from '@/components/dashboard/real-time-events-stream'
import { TimeSavedCounter } from '@/components/dashboard/time-saved-counter'
import { CalendarOptimizationView } from '@/components/dashboard/calendar-optimization-view'
import { AIAvatarControlCenter } from '@/components/dashboard/ai-avatar-control-center'

const formatTime = (hours: number) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`
  }
  return `${hours.toFixed(1)}h`
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const recentActivities = [
  {
    id: 1,
    type: 'optimization',
    title: 'Meeting moved to protect focus time',
    time: '2 minutes ago',
    impact: 'High',
    details: 'Moved "Product Review" from 2pm to 4pm to protect coding block'
  },
  {
    id: 2,
    type: 'analysis',
    title: 'Weekly standup analyzed',
    time: '15 minutes ago',
    impact: 'Medium',
    details: 'Detected 18% efficiency gain opportunity'
  },
  {
    id: 3,
    type: 'suggestion',
    title: 'Break reminder scheduled',
    time: '1 hour ago',
    impact: 'Low',
    details: 'AI suggests 15min break after 3-hour focus session'
  },
  {
    id: 4,
    type: 'conflict',
    title: 'Calendar conflict resolved',
    time: '2 hours ago',
    impact: 'High',
    details: 'Automatically rescheduled overlapping meetings'
  },
]

export function DashboardOverview() {
  const {
    aiStatus,
    productivityMetrics,
    connected,
    timeSaved,
    realTimeEvents,
    demoMode,
    toggleDemoMode,
    avatarPersonality,
    setAvatarPersonality
  } = useSocket()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [costSavings, setCostSavings] = useState(0)
  const [efficiency, setEfficiency] = useState(94)
  const [meetingsOptimized, setMeetingsOptimized] = useState(12)

  // Calculate real-time metrics
  useEffect(() => {
    // Calculate cost savings based on time saved (assuming $75/hour average)
    setCostSavings(timeSaved * 75)

    // Update efficiency based on optimization events
    const recentOptimizations = realTimeEvents.filter(
      event => event.type === 'optimization' &&
      Date.now() - event.timestamp.getTime() < 24 * 60 * 60 * 1000 // Last 24h
    )
    setMeetingsOptimized(recentOptimizations.length + 12) // Base number plus new ones

    // Efficiency calculation
    const baseEfficiency = 85
    const bonusEfficiency = Math.min(recentOptimizations.length * 2, 15)
    setEfficiency(baseEfficiency + bonusEfficiency)
  }, [timeSaved, realTimeEvents])

  const statCards = [
    {
      title: 'Time Saved Today',
      value: formatTime(timeSaved),
      change: `+${Math.round((timeSaved / 8) * 100)}%`,
      changeType: 'positive' as const,
      icon: Clock,
      color: 'from-blue-500 to-cyan-500',
      description: 'From AI optimization',
      realTime: true
    },
    {
      title: 'Cost Savings',
      value: formatCurrency(costSavings),
      change: '+$1,250 weekly',
      changeType: 'positive' as const,
      icon: DollarSign,
      color: 'from-green-500 to-emerald-500',
      description: 'ROI from automation',
      realTime: true
    },
    {
      title: 'Meeting Efficiency',
      value: `${efficiency}%`,
      change: `+${efficiency - 85}%`,
      changeType: 'positive' as const,
      icon: Target,
      color: 'from-purple-500 to-pink-500',
      description: 'Average meeting score',
      realTime: true
    },
    {
      title: 'AI Interventions',
      value: meetingsOptimized.toString(),
      change: `${realTimeEvents.length} recent`,
      changeType: 'neutral' as const,
      icon: Brain,
      color: 'from-orange-500 to-red-500',
      description: 'Autonomous decisions',
      realTime: true
    },
  ]

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="space-y-6">
      {/* Header with Demo Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              MeetingAssassin Dashboard
            </h1>
            {demoMode && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center space-x-2 px-3 py-1 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-full border border-purple-500/20"
              >
                <Sparkles className="w-4 h-4 text-purple-500" />
                <span className="text-xs font-medium text-purple-600 dark:text-purple-400">
                  DEMO MODE
                </span>
              </motion.div>
            )}
          </div>
          <p className="text-muted-foreground mt-2">
            {currentTime.toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Demo Mode Toggle */}
          <Button
            variant={demoMode ? "default" : "outline"}
            size="sm"
            onClick={toggleDemoMode}
            className={demoMode ? "bg-purple-500 hover:bg-purple-600" : ""}
          >
            {demoMode ? <PauseCircle className="w-4 h-4 mr-2" /> : <PlayCircle className="w-4 h-4 mr-2" />}
            {demoMode ? 'Pause Demo' : 'Start Demo'}
          </Button>

          {/* Connection Status */}
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full ${
            connected || demoMode ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'
          }`}>
            <div className={`w-2 h-2 rounded-full animate-pulse ${
              connected || demoMode ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className={`text-xs font-medium ${
              connected || demoMode ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'
            }`}>
              AI {connected || demoMode ? 'Active' : 'Disconnected'}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Real-time Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glass-card glow-effect hover:scale-105 transition-all duration-300 relative overflow-hidden">
              <CardContent className="p-6 relative">
                {/* Real-time indicator */}
                {stat.realTime && (
                  <motion.div
                    className="absolute top-2 right-2 w-2 h-2 bg-green-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                )}

                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${stat.color} flex items-center justify-center relative`}>
                    <stat.icon className="w-6 h-6 text-white" />
                    {stat.realTime && (
                      <motion.div
                        className="absolute inset-0 rounded-xl bg-white/20"
                        animate={{ opacity: [0, 0.3, 0] }}
                        transition={{ repeat: Infinity, duration: 3 }}
                      />
                    )}
                  </div>
                  <Badge
                    variant={stat.changeType === 'positive' ? 'default' : 'secondary'}
                    className={stat.changeType === 'positive' ? 'bg-green-500/10 text-green-600 dark:text-green-400' : ''}
                  >
                    {stat.change}
                  </Badge>
                </div>
                <div>
                  <motion.h3
                    className="text-2xl font-bold mb-1"
                    key={stat.value}
                    initial={{ scale: 1.1 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", duration: 0.5 }}
                  >
                    {stat.value}
                  </motion.h3>
                  <p className="text-sm text-muted-foreground mb-1">{stat.title}</p>
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Enhanced Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Calendar Optimization Visualization */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-8"
        >
          <CalendarOptimizationView />
        </motion.div>

        {/* Real-time Events Stream */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="lg:col-span-4"
        >
          <RealTimeEventsStream events={realTimeEvents} />
        </motion.div>
      </div>

      {/* Second Row: AI Avatar Control & Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Avatar Control Center */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <AIAvatarControlCenter
            personality={avatarPersonality}
            onPersonalityChange={setAvatarPersonality}
            aiStatus={aiStatus}
            connected={connected || demoMode}
          />
        </motion.div>

        {/* Productivity Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
        >
          <ProductivityMetricsWidget
            metrics={productivityMetrics}
            timeSaved={timeSaved}
            costSavings={costSavings}
          />
        </motion.div>
      </div>

      {/* Time Saved Counter - Prominent Display */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1.2 }}
      >
        <TimeSavedCounter timeSaved={timeSaved} costSavings={costSavings} />
      </motion.div>

      {/* Enhanced Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.4 }}
      >
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                <span>AI Control Center</span>
              </div>
              <Badge variant="outline" className="text-xs">
                {realTimeEvents.length} Active
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Button
                className="h-auto p-4 bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 text-white relative overflow-hidden"
                onClick={() => {}}
              >
                <motion.div
                  className="absolute inset-0 bg-white/20"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
                />
                <div className="text-center relative z-10">
                  <Target className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-semibold">Optimize Now</div>
                  <div className="text-xs opacity-90">Genetic algorithm</div>
                </div>
              </Button>

              <Button
                variant="outline"
                className="h-auto p-4 hover:bg-green-50 dark:hover:bg-green-950/20"
                onClick={() => {}}
              >
                <div className="text-center">
                  <Users className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-semibold">Smart Schedule</div>
                  <div className="text-xs text-muted-foreground">AI assistant</div>
                </div>
              </Button>

              <Button
                variant="outline"
                className="h-auto p-4 hover:bg-orange-50 dark:hover:bg-orange-950/20"
                onClick={() => {}}
              >
                <div className="text-center">
                  <LineChart className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-semibold">Analytics</div>
                  <div className="text-xs text-muted-foreground">Deep insights</div>
                </div>
              </Button>

              <Button
                variant="outline"
                className="h-auto p-4 hover:bg-blue-50 dark:hover:bg-blue-950/20"
                onClick={toggleDemoMode}
              >
                <div className="text-center">
                  <RotateCcw className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-semibold">Reset Demo</div>
                  <div className="text-xs text-muted-foreground">Fresh start</div>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}