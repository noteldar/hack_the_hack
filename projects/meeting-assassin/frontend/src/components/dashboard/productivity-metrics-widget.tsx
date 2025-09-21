'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  Clock,
  Target,
  Calendar,
  DollarSign,
  BarChart3,
  PieChart,
  Activity,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ProductivityMetrics } from '@/lib/socket'

interface ProductivityMetricsWidgetProps {
  metrics: ProductivityMetrics | null
  timeSaved: number
  costSavings: number
}

const generateMockChartData = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  return days.map((day, index) => ({
    day,
    focusTime: 3 + Math.random() * 3,
    meetingTime: 2 + Math.random() * 2,
    efficiency: 70 + Math.random() * 25
  }))
}

export function ProductivityMetricsWidget({
  metrics,
  timeSaved,
  costSavings
}: ProductivityMetricsWidgetProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'goals'>('overview')
  const [chartData] = useState(generateMockChartData())

  // Use mock data for demo purposes
  const displayMetrics = metrics || {
    daily: {
      focusTime: 4.2,
      meetingTime: 2.8,
      breakTime: 1.0,
      efficiency: 87
    },
    weekly: {
      totalHours: 42,
      productiveHours: 36.5,
      meetingHours: 14,
      focusHours: 22.5,
      trend: 'up' as const
    },
    goals: {
      focusTimeGoal: 6,
      meetingLimitGoal: 3,
      efficiencyGoal: 85,
      current: {
        focusTime: 4.2,
        meetingCount: 2.8,
        efficiency: 87
      }
    }
  }

  const focusTimeProgress = (displayMetrics.goals.current.focusTime / displayMetrics.goals.focusTimeGoal) * 100
  const meetingProgress = ((displayMetrics.goals.meetingLimitGoal - displayMetrics.goals.current.meetingCount) / displayMetrics.goals.meetingLimitGoal) * 100
  const efficiencyProgress = (displayMetrics.goals.current.efficiency / displayMetrics.goals.efficiencyGoal) * 100

  const formatTime = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}m`
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

  return (
    <Card className="glass-card h-full">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ repeat: Infinity, duration: 4 }}
            >
              <BarChart3 className="w-5 h-5 text-green-500" />
            </motion.div>
            <span>Productivity Analytics</span>
          </div>
          <Badge className={`${
            displayMetrics.weekly.trend === 'up'
              ? 'bg-green-500/10 text-green-600 dark:text-green-400'
              : 'bg-red-500/10 text-red-600 dark:text-red-400'
          }`}>
            {displayMetrics.weekly.trend === 'up' ? '↗ Trending Up' : '↘ Trending Down'}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'overview' | 'trends' | 'goals')} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="goals">Goals</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <motion.div
                className="p-3 rounded-xl bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                    Focus Time Today
                  </span>
                </div>
                <div className="text-2xl font-bold">{formatTime(displayMetrics.daily.focusTime)}</div>
                <div className="text-xs text-muted-foreground">
                  +{formatTime(timeSaved)} from AI optimization
                </div>
              </motion.div>

              <motion.div
                className="p-3 rounded-xl bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    Efficiency Score
                  </span>
                </div>
                <div className="text-2xl font-bold">{displayMetrics.daily.efficiency}%</div>
                <div className="text-xs text-muted-foreground">
                  Above target of 85%
                </div>
              </motion.div>

              <motion.div
                className="p-3 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Calendar className="w-4 h-4 text-purple-500" />
                  <span className="text-sm font-medium text-purple-600 dark:text-purple-400">
                    Meeting Time
                  </span>
                </div>
                <div className="text-2xl font-bold">{formatTime(displayMetrics.daily.meetingTime)}</div>
                <div className="text-xs text-muted-foreground">
                  Under 3h daily limit
                </div>
              </motion.div>

              <motion.div
                className="p-3 rounded-xl bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <DollarSign className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-medium text-orange-600 dark:text-orange-400">
                    Value Generated
                  </span>
                </div>
                <div className="text-2xl font-bold">{formatCurrency(costSavings)}</div>
                <div className="text-xs text-muted-foreground">
                  From time optimization
                </div>
              </motion.div>
            </div>

            {/* Weekly Summary */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 border border-gray-200/50 dark:border-gray-700/50">
              <h4 className="font-medium mb-3 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-indigo-500" />
                Weekly Summary
              </h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="flex justify-between mb-1">
                    <span>Total Hours</span>
                    <span className="font-bold">{displayMetrics.weekly.totalHours}h</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Productive Hours</span>
                    <span className="font-bold text-green-600 dark:text-green-400">
                      {displayMetrics.weekly.productiveHours}h
                    </span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span>Focus Hours</span>
                    <span className="font-bold">{displayMetrics.weekly.focusHours}h</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Meeting Hours</span>
                    <span className="font-bold text-blue-600 dark:text-blue-400">
                      {displayMetrics.weekly.meetingHours}h
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="trends" className="space-y-4 mt-4">
            {/* Weekly Trend Chart */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-500/5 to-purple-500/5 border border-indigo-500/20">
              <h4 className="font-medium mb-4 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2 text-indigo-500" />
                Weekly Productivity Trends
              </h4>

              <div className="space-y-4">
                {chartData.map((data, index) => (
                  <motion.div
                    key={data.day}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="space-y-2"
                  >
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{data.day}</span>
                      <span className="text-muted-foreground">{data.efficiency.toFixed(0)}% efficiency</span>
                    </div>

                    <div className="flex space-x-2 h-4">
                      <div
                        className="bg-blue-500 rounded-sm flex-shrink-0"
                        style={{ width: `${(data.focusTime / 8) * 100}%` }}
                        title={`Focus: ${formatTime(data.focusTime)}`}
                      />
                      <div
                        className="bg-purple-500 rounded-sm flex-shrink-0"
                        style={{ width: `${(data.meetingTime / 8) * 100}%` }}
                        title={`Meetings: ${formatTime(data.meetingTime)}`}
                      />
                      <div className="bg-gray-200 dark:bg-gray-700 rounded-sm flex-1" />
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="flex items-center justify-center space-x-4 mt-4 text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-blue-500 rounded-sm" />
                  <span>Focus Time</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-purple-500 rounded-sm" />
                  <span>Meetings</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-sm" />
                  <span>Available</span>
                </div>
              </div>
            </div>

            {/* Improvement Insights */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm">AI Insights</h4>
              {[
                { text: 'Best focus time: 9-11 AM (94% efficiency)', type: 'positive' },
                { text: 'Meeting clustering improved by 23%', type: 'positive' },
                { text: 'Context switching reduced by 31%', type: 'positive' },
                { text: 'Recommend 15min buffer between meetings', type: 'neutral' }
              ].map((insight, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-2 rounded-lg text-xs ${
                    insight.type === 'positive'
                      ? 'bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20'
                      : 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'
                  }`}
                >
                  {insight.text}
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="goals" className="space-y-4 mt-4">
            {/* Goal Progress */}
            <div className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Daily Focus Time Goal</span>
                  <span className="text-sm text-muted-foreground">
                    {formatTime(displayMetrics.goals.current.focusTime)} / {formatTime(displayMetrics.goals.focusTimeGoal)}
                  </span>
                </div>
                <Progress value={focusTimeProgress} className="h-2" />
                <div className="text-xs text-muted-foreground">
                  {focusTimeProgress >= 100 ? '✅ Goal achieved!' : `${(100 - focusTimeProgress).toFixed(0)}% to go`}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Meeting Time Limit</span>
                  <span className="text-sm text-muted-foreground">
                    {formatTime(displayMetrics.goals.current.meetingCount)} / {formatTime(displayMetrics.goals.meetingLimitGoal)} limit
                  </span>
                </div>
                <Progress value={Math.max(0, meetingProgress)} className="h-2" />
                <div className="text-xs text-muted-foreground">
                  {meetingProgress >= 100 ? '✅ Under meeting limit!' : '⚠️ Approaching meeting limit'}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Efficiency Target</span>
                  <span className="text-sm text-muted-foreground">
                    {displayMetrics.goals.current.efficiency}% / {displayMetrics.goals.efficiencyGoal}%
                  </span>
                </div>
                <Progress value={efficiencyProgress} className="h-2" />
                <div className="text-xs text-muted-foreground">
                  {efficiencyProgress >= 100 ? '✅ Target exceeded!' : `${(displayMetrics.goals.efficiencyGoal - displayMetrics.goals.current.efficiency).toFixed(0)}% to target`}
                </div>
              </div>
            </div>

            {/* Goal Achievements */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-yellow-500/5 to-orange-500/5 border border-yellow-500/20">
              <h4 className="font-medium mb-3 flex items-center">
                <Zap className="w-4 h-4 mr-2 text-yellow-500" />
                Recent Achievements
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span>7-day focus time streak</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <span>Meeting efficiency above 85%</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full" />
                  <span>Zero calendar conflicts this week</span>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}