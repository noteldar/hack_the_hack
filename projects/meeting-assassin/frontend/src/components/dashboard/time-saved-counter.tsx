'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Clock, DollarSign, TrendingUp, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface TimeSavedCounterProps {
  timeSaved: number
  costSavings: number
}

export function TimeSavedCounter({ timeSaved, costSavings }: TimeSavedCounterProps) {
  const [displayTime, setDisplayTime] = useState(0)
  const [displayCost, setDisplayCost] = useState(0)
  const [weeklyProjection, setWeeklyProjection] = useState(0)
  const [monthlyProjection, setMonthlyProjection] = useState(0)

  // Animate counter updates
  useEffect(() => {
    const increment = timeSaved / 50 // Smooth animation over 50 steps
    const costIncrement = costSavings / 50

    const timer = setInterval(() => {
      setDisplayTime(prev => {
        const next = prev + increment
        return next >= timeSaved ? timeSaved : next
      })
      setDisplayCost(prev => {
        const next = prev + costIncrement
        return next >= costSavings ? costSavings : next
      })
    }, 50)

    return () => clearInterval(timer)
  }, [timeSaved, costSavings])

  // Calculate projections
  useEffect(() => {
    const hoursPerDay = timeSaved
    setWeeklyProjection(hoursPerDay * 5) // 5 work days
    setMonthlyProjection(hoursPerDay * 22) // ~22 work days
  }, [timeSaved])

  const formatTime = (hours: number) => {
    const h = Math.floor(hours)
    const m = Math.floor((hours - h) * 60)
    const s = Math.floor(((hours - h) * 60 - m) * 60)

    if (h > 0) return `${h}h ${m}m ${s}s`
    if (m > 0) return `${m}m ${s}s`
    return `${s}s`
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const progressToday = Math.min((timeSaved / 8) * 100, 100) // 8h = 100%
  const progressWeek = Math.min((weeklyProjection / 40) * 100, 100) // 40h = 100%

  return (
    <Card className="glass-card relative overflow-hidden">
      {/* Animated background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5"
        animate={{
          background: [
            'linear-gradient(to right, rgba(147, 51, 234, 0.05), rgba(59, 130, 246, 0.05))',
            'linear-gradient(to right, rgba(59, 130, 246, 0.05), rgba(16, 185, 129, 0.05))',
            'linear-gradient(to right, rgba(16, 185, 129, 0.05), rgba(147, 51, 234, 0.05))'
          ]
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
      />

      <CardHeader className="relative z-10">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-6 h-6 text-purple-500" />
            </motion.div>
            <span className="text-xl font-bold">Time Liberation Dashboard</span>
          </CardTitle>
          <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 animate-pulse">
            LIVE
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 relative z-10">
        {/* Main counter display */}
        <div className="text-center space-y-4">
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Time Saved Today
            </h3>
            <motion.div
              className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent"
              key={displayTime}
              initial={{ scale: 1.1 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              {formatTime(displayTime)}
            </motion.div>
            <Progress
              value={progressToday}
              className="h-3 bg-gray-200 dark:bg-gray-800"
            />
            <p className="text-sm text-muted-foreground">
              {progressToday.toFixed(1)}% of daily productivity goal
            </p>
          </div>

          {/* Cost savings */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              <span className="text-sm font-medium text-green-600 dark:text-green-400">
                Cost Savings
              </span>
            </div>
            <motion.div
              className="text-3xl font-bold text-green-600 dark:text-green-400"
              key={displayCost}
              initial={{ scale: 1.1 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              {formatCurrency(displayCost)}
            </motion.div>
          </div>
        </div>

        {/* Projections grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="text-center p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
            <div className="flex items-center justify-center space-x-1 mb-2">
              <Clock className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                Weekly Projection
              </span>
            </div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {formatTime(weeklyProjection)}
            </div>
            <Progress
              value={progressWeek}
              className="h-2 mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {formatCurrency(weeklyProjection * 75)} saved
            </p>
          </div>

          <div className="text-center p-4 rounded-xl bg-purple-500/5 border border-purple-500/20">
            <div className="flex items-center justify-center space-x-1 mb-2">
              <TrendingUp className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium text-purple-600 dark:text-purple-400">
                Monthly Projection
              </span>
            </div>
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {formatTime(monthlyProjection)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatCurrency(monthlyProjection * 75)} potential
            </p>
          </div>
        </div>

        {/* ROI Calculator */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium mb-3 text-center">ROI Analysis</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-green-600 dark:text-green-400">
                {Math.round((costSavings / 500) * 100)}%
              </div>
              <p className="text-xs text-muted-foreground">ROI</p>
            </div>
            <div>
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {Math.round(timeSaved * 4)}
              </div>
              <p className="text-xs text-muted-foreground">Meetings Optimized</p>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                {Math.round((timeSaved / 8) * 100)}%
              </div>
              <p className="text-xs text-muted-foreground">Efficiency Gain</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}