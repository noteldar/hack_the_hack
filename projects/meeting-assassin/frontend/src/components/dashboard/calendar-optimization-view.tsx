'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Clock,
  Target,
  TrendingUp,
  Zap,
  RefreshCw,
  Play,
  Pause,
  SkipForward,
  ChevronRight,
  BarChart3,
  Activity,
  Brain
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface Meeting {
  id: string
  title: string
  start: string
  end: string
  duration: number
  priority: 'high' | 'medium' | 'low'
  type: 'meeting' | 'focus' | 'break'
  optimized?: boolean
  originalStart?: string
  participants: number
  conflicted?: boolean
}

interface GeneticAlgorithmState {
  generation: number
  bestFitness: number
  averageFitness: number
  isRunning: boolean
  convergence: number
  improvements: string[]
}

export function CalendarOptimizationView() {
  const [activeTab, setActiveTab] = useState<'calendar' | 'algorithm' | 'analytics'>('calendar')
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [geneticState, setGeneticState] = useState<GeneticAlgorithmState>({
    generation: 0,
    bestFitness: 0.65,
    averageFitness: 0.45,
    isRunning: false,
    convergence: 0,
    improvements: []
  })

  const [beforeMeetings] = useState<Meeting[]>([
    {
      id: '1',
      title: 'Team Standup',
      start: '09:00',
      end: '09:30',
      duration: 30,
      priority: 'high',
      type: 'meeting',
      participants: 8,
      conflicted: true
    },
    {
      id: '2',
      title: 'Deep Work Block',
      start: '09:30',
      end: '11:30',
      duration: 120,
      priority: 'high',
      type: 'focus',
      participants: 1,
      conflicted: true
    },
    {
      id: '3',
      title: 'Client Review',
      start: '10:00',
      end: '11:00',
      duration: 60,
      priority: 'medium',
      type: 'meeting',
      participants: 4,
      conflicted: true
    },
    {
      id: '4',
      title: 'Planning Session',
      start: '14:00',
      end: '15:30',
      duration: 90,
      priority: 'medium',
      type: 'meeting',
      participants: 6
    },
    {
      id: '5',
      title: 'Focus Time',
      start: '16:00',
      end: '17:00',
      duration: 60,
      priority: 'high',
      type: 'focus',
      participants: 1
    }
  ])

  const [afterMeetings] = useState<Meeting[]>([
    {
      id: '1',
      title: 'Team Standup',
      start: '09:00',
      end: '09:30',
      duration: 30,
      priority: 'high',
      type: 'meeting',
      participants: 8,
      optimized: false
    },
    {
      id: '2',
      title: 'Deep Work Block',
      start: '09:30',
      end: '12:00',
      duration: 150,
      priority: 'high',
      type: 'focus',
      participants: 1,
      optimized: true,
      originalStart: '09:30'
    },
    {
      id: '3',
      title: 'Client Review',
      start: '13:00',
      end: '14:00',
      duration: 60,
      priority: 'medium',
      type: 'meeting',
      participants: 4,
      optimized: true,
      originalStart: '10:00'
    },
    {
      id: '4',
      title: 'Planning Session',
      start: '14:00',
      end: '15:30',
      duration: 90,
      priority: 'medium',
      type: 'meeting',
      participants: 6,
      optimized: false
    },
    {
      id: '5',
      title: 'Focus Time',
      start: '15:30',
      end: '17:00',
      duration: 90,
      priority: 'high',
      type: 'focus',
      participants: 1,
      optimized: true,
      originalStart: '16:00'
    }
  ])

  // Simulate genetic algorithm
  useEffect(() => {
    if (isOptimizing) {
      const interval = setInterval(() => {
        setGeneticState(prev => {
          const newGeneration = prev.generation + 1
          const fitnessImprovement = Math.random() * 0.02
          const newBestFitness = Math.min(prev.bestFitness + fitnessImprovement, 1.0)
          const newAverageFitness = Math.min(prev.averageFitness + fitnessImprovement * 0.7, newBestFitness - 0.05)
          const convergence = Math.min((newGeneration / 50) * 100, 100)

          const improvements = [
            'Resolved conflict between Deep Work and Client Review',
            'Extended focus blocks for better productivity',
            'Optimized meeting clustering',
            'Minimized context switching',
            'Protected high-energy time slots'
          ]

          return {
            generation: newGeneration,
            bestFitness: newBestFitness,
            averageFitness: newAverageFitness,
            isRunning: newGeneration < 50,
            convergence,
            improvements: improvements.slice(0, Math.floor(newGeneration / 10))
          }
        })
      }, 200)

      return () => clearInterval(interval)
    }
  }, [isOptimizing])

  const handleOptimize = () => {
    setIsOptimizing(true)
    setGeneticState(prev => ({ ...prev, isRunning: true, generation: 0 }))
    setTimeout(() => {
      setIsOptimizing(false)
    }, 10000) // Stop after 10 seconds
  }

  const getMeetingColor = (meeting: Meeting) => {
    if (meeting.conflicted) return 'bg-red-500/20 border-red-500'
    if (meeting.optimized) return 'bg-purple-500/20 border-purple-500'
    if (meeting.type === 'focus') return 'bg-blue-500/20 border-blue-500'
    return 'bg-gray-500/20 border-gray-500'
  }

  const renderMeetingBlock = (meeting: Meeting, isAfter = false) => (
    <motion.div
      key={meeting.id}
      initial={isAfter && meeting.optimized ? { scale: 0, rotate: -10 } : {}}
      animate={isAfter && meeting.optimized ? { scale: 1, rotate: 0 } : {}}
      transition={{ type: "spring", delay: 0.2 }}
      className={`p-3 rounded-lg border-2 ${getMeetingColor(meeting)} relative overflow-hidden`}
    >
      {meeting.optimized && (
        <motion.div
          className="absolute inset-0 bg-purple-400/10"
          animate={{ opacity: [0, 0.3, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        />
      )}

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-1">
          <span className="font-medium text-sm">{meeting.title}</span>
          {meeting.optimized && (
            <Badge className="bg-purple-500/10 text-purple-600 dark:text-purple-400 text-xs">
              Optimized
            </Badge>
          )}
          {meeting.conflicted && (
            <Badge variant="destructive" className="text-xs">
              Conflict
            </Badge>
          )}
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{meeting.start} - {meeting.end}</span>
          <span>{meeting.duration}m</span>
        </div>
        {meeting.originalStart && meeting.originalStart !== meeting.start && (
          <div className="text-xs text-purple-600 dark:text-purple-400 mt-1">
            Moved from {meeting.originalStart}
          </div>
        )}
      </div>
    </motion.div>
  )

  return (
    <Card className="glass-card h-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <motion.div
              animate={{ rotate: isOptimizing ? 360 : 0 }}
              transition={{ duration: 2, repeat: isOptimizing ? Infinity : 0 }}
            >
              <Brain className="w-5 h-5 text-purple-500" />
            </motion.div>
            <span>Calendar Optimization Engine</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button
              variant={isOptimizing ? "destructive" : "default"}
              size="sm"
              onClick={handleOptimize}
              disabled={isOptimizing}
              className={!isOptimizing ? "bg-purple-500 hover:bg-purple-600" : ""}
            >
              {isOptimizing ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Optimizing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Run Optimization
                </>
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'calendar' | 'algorithm' | 'analytics')} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="calendar">Calendar View</TabsTrigger>
            <TabsTrigger value="algorithm">Genetic Algorithm</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="calendar" className="space-y-4 mt-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Before Optimization */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-sm">Before Optimization</h3>
                  <Badge variant="destructive" className="text-xs">3 Conflicts</Badge>
                </div>
                <div className="space-y-2">
                  {beforeMeetings.map(meeting => renderMeetingBlock(meeting, false))}
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  Efficiency Score: 65% • Focus Time: 3h
                </div>
              </div>

              {/* After Optimization */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-sm">After Optimization</h3>
                  <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 text-xs">
                    0 Conflicts
                  </Badge>
                </div>
                <div className="space-y-2">
                  <AnimatePresence>
                    {afterMeetings.map(meeting => renderMeetingBlock(meeting, true))}
                  </AnimatePresence>
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 mt-2">
                  Efficiency Score: 94% • Focus Time: 4h • +29% improvement
                </div>
              </div>
            </div>

            {/* Optimization Summary */}
            <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-purple-500/5 to-blue-500/5 border border-purple-500/20">
              <h4 className="font-medium mb-3 flex items-center">
                <Target className="w-4 h-4 mr-2 text-purple-500" />
                Optimization Results
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">+1.2h</div>
                  <p className="text-muted-foreground">Focus Time Added</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600 dark:text-blue-400">3</div>
                  <p className="text-muted-foreground">Conflicts Resolved</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600 dark:text-purple-400">29%</div>
                  <p className="text-muted-foreground">Efficiency Gain</p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="algorithm" className="space-y-4 mt-4">
            {/* Algorithm Status */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/5 to-indigo-500/5 border border-blue-500/20">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium">Genetic Algorithm Status</h4>
                <Badge
                  variant={geneticState.isRunning ? "default" : "secondary"}
                  className={geneticState.isRunning ? "bg-green-500/10 text-green-600 dark:text-green-400" : ""}
                >
                  {geneticState.isRunning ? 'Running' : 'Idle'}
                </Badge>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span>Generation</span>
                  <span className="font-mono font-bold">{geneticState.generation}/50</span>
                </div>
                <Progress value={(geneticState.generation / 50) * 100} className="h-2" />

                <div className="flex items-center justify-between text-sm">
                  <span>Best Fitness</span>
                  <span className="font-mono font-bold">{(geneticState.bestFitness * 100).toFixed(1)}%</span>
                </div>
                <Progress value={geneticState.bestFitness * 100} className="h-2" />

                <div className="flex items-center justify-between text-sm">
                  <span>Average Fitness</span>
                  <span className="font-mono font-bold">{(geneticState.averageFitness * 100).toFixed(1)}%</span>
                </div>
                <Progress value={geneticState.averageFitness * 100} className="h-2" />

                <div className="flex items-center justify-between text-sm">
                  <span>Convergence</span>
                  <span className="font-mono font-bold">{geneticState.convergence.toFixed(1)}%</span>
                </div>
                <Progress value={geneticState.convergence} className="h-2" />
              </div>
            </div>

            {/* Algorithm Improvements */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Optimization Steps</h4>
              <AnimatePresence>
                {geneticState.improvements.map((improvement, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex items-center space-x-3 p-3 rounded-lg bg-green-500/5 border border-green-500/20"
                  >
                    <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold">
                      {index + 1}
                    </div>
                    <span className="text-sm">{improvement}</span>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4 mt-4">
            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-gradient-to-r from-green-500/5 to-emerald-500/5 border border-green-500/20">
                <div className="flex items-center space-x-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <h4 className="font-medium">Productivity Gains</h4>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Focus Time Increase</span>
                    <span className="font-bold text-green-600 dark:text-green-400">+33%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Meeting Efficiency</span>
                    <span className="font-bold text-green-600 dark:text-green-400">+29%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Context Switching</span>
                    <span className="font-bold text-green-600 dark:text-green-400">-45%</span>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 border border-blue-500/20">
                <div className="flex items-center space-x-2 mb-3">
                  <BarChart3 className="w-4 h-4 text-blue-500" />
                  <h4 className="font-medium">Schedule Quality</h4>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Conflicts Resolved</span>
                    <span className="font-bold text-blue-600 dark:text-blue-400">100%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Optimal Scheduling</span>
                    <span className="font-bold text-blue-600 dark:text-blue-400">94%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Time Utilization</span>
                    <span className="font-bold text-blue-600 dark:text-blue-400">87%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Weekly Trend */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/5 to-pink-500/5 border border-purple-500/20">
              <h4 className="font-medium mb-3">Weekly Optimization Impact</h4>
              <div className="grid grid-cols-7 gap-2 mb-3">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
                  <div key={day} className="text-center">
                    <div className="text-xs text-muted-foreground mb-1">{day}</div>
                    <div className={`h-12 rounded bg-gradient-to-t ${
                      index < 5 ? 'from-purple-500 to-purple-400' : 'from-gray-300 to-gray-200'
                    }`} style={{
                      height: `${30 + (index < 5 ? Math.random() * 20 : 0)}px`
                    }} />
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground text-center">
                Average optimization score across the week
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}