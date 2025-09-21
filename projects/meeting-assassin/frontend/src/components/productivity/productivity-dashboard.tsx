'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  Clock,
  Target,
  Zap,
  Calendar,
  Users,
  BarChart3,
  PieChart,
  Activity,
  Award
} from 'lucide-react'
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const weeklyData = [
  { day: 'Mon', focusTime: 6.5, meetingTime: 2.5, efficiency: 85, productivity: 90 },
  { day: 'Tue', focusTime: 7.2, meetingTime: 1.8, efficiency: 92, productivity: 88 },
  { day: 'Wed', focusTime: 5.8, meetingTime: 3.2, efficiency: 78, productivity: 75 },
  { day: 'Thu', focusTime: 6.9, meetingTime: 2.1, efficiency: 88, productivity: 85 },
  { day: 'Fri', focusTime: 4.5, meetingTime: 4.5, efficiency: 65, productivity: 70 },
  { day: 'Sat', focusTime: 3.0, meetingTime: 0.5, efficiency: 95, productivity: 60 },
  { day: 'Sun', focusTime: 2.5, meetingTime: 0, efficiency: 98, productivity: 45 }
]

const timeDistribution = [
  { name: 'Deep Work', value: 35, color: '#8b5cf6' },
  { name: 'Meetings', value: 25, color: '#3b82f6' },
  { name: 'Communication', value: 15, color: '#10b981' },
  { name: 'Admin Tasks', value: 15, color: '#f59e0b' },
  { name: 'Breaks', value: 10, color: '#ef4444' }
]

const performanceMetrics = [
  { metric: 'Focus Quality', current: 85, target: 90, fullMark: 100 },
  { metric: 'Meeting Efficiency', current: 78, target: 85, fullMark: 100 },
  { metric: 'Response Time', current: 92, target: 90, fullMark: 100 },
  { metric: 'Goal Achievement', current: 88, target: 95, fullMark: 100 },
  { metric: 'Work-Life Balance', current: 75, target: 80, fullMark: 100 },
  { metric: 'Energy Levels', current: 82, target: 85, fullMark: 100 }
]

const goals = [
  {
    title: 'Daily Focus Time',
    current: 6.2,
    target: 8,
    unit: 'hours',
    progress: 77.5,
    trend: 'up',
    color: 'from-purple-500 to-pink-500'
  },
  {
    title: 'Meeting Limit',
    current: 4,
    target: 3,
    unit: 'meetings',
    progress: 25, // Inverse - less is better
    trend: 'down',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    title: 'Weekly Efficiency',
    current: 84,
    target: 90,
    unit: '%',
    progress: 93.3,
    trend: 'up',
    color: 'from-green-500 to-emerald-500'
  },
  {
    title: 'Response Rate',
    current: 95,
    target: 90,
    unit: '%',
    progress: 100,
    trend: 'stable',
    color: 'from-orange-500 to-red-500'
  }
]

export function ProductivityDashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [animateCharts, setAnimateCharts] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setAnimateCharts(true), 500)
    return () => clearTimeout(timer)
  }, [])

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ dataKey: string; value: number; color: string }>; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card p-3 border border-white/20">
          <p className="font-semibold">{label}</p>
          {payload.map((entry: { dataKey: string; value: number; color: string }, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}${
                entry.dataKey.includes('Time') ? 'h' :
                entry.dataKey.includes('efficiency') || entry.dataKey.includes('productivity') ? '%' : ''
              }`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Productivity Analytics
          </h1>
          <p className="text-muted-foreground mt-2">
            AI-powered insights into your work patterns and efficiency
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Badge className="bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300">
            <Award className="w-3 h-3 mr-1" />
            Top 10% Performer
          </Badge>
        </div>
      </motion.div>

      {/* Goal Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {goals.map((goal, index) => (
          <motion.div
            key={goal.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glass-card glow-effect">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${goal.color} flex items-center justify-center`}>
                    {goal.title.includes('Focus') && <Clock className="w-6 h-6 text-white" />}
                    {goal.title.includes('Meeting') && <Users className="w-6 h-6 text-white" />}
                    {goal.title.includes('Efficiency') && <TrendingUp className="w-6 h-6 text-white" />}
                    {goal.title.includes('Response') && <Zap className="w-6 h-6 text-white" />}
                  </div>
                  <Badge variant={goal.trend === 'up' ? 'default' : goal.trend === 'down' ? 'destructive' : 'secondary'}>
                    {goal.trend === 'up' ? '↗' : goal.trend === 'down' ? '↘' : '→'}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-bold">{goal.current}</span>
                    <span className="text-sm text-muted-foreground">/ {goal.target} {goal.unit}</span>
                  </div>
                  <p className="text-sm font-medium">{goal.title}</p>
                  <Progress value={goal.progress} className="h-2" />
                  <p className="text-xs text-muted-foreground">
                    {goal.progress.toFixed(1)}% of target achieved
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Main Analytics */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4 lg:w-96">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="time">Time Analysis</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Weekly Trend */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-purple-500" />
                    <span>Weekly Productivity Trend</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={weeklyData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="focusTime" fill="#8b5cf6" name="Focus Time" radius={4} />
                      <Bar dataKey="meetingTime" fill="#3b82f6" name="Meeting Time" radius={4} />
                      <Line
                        type="monotone"
                        dataKey="efficiency"
                        stroke="#10b981"
                        strokeWidth={3}
                        name="Efficiency"
                        dot={{ fill: '#10b981', r: 4 }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Time Distribution */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <PieChart className="w-5 h-5 text-blue-500" />
                    <span>Time Distribution</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <RechartsPieChart>
                      <Pie
                        dataKey="value"
                        data={timeDistribution}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        innerRadius={40}
                        paddingAngle={5}
                      >
                        {timeDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    {timeDistribution.map((item, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-xs">{item.name}: {item.value}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-green-500" />
                  <span>Performance Radar</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart data={performanceMetrics}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar
                      name="Current"
                      dataKey="current"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                    <Radar
                      name="Target"
                      dataKey="target"
                      stroke="#10b981"
                      fill="transparent"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* AI Insights */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  <span>AI Insights</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  {
                    type: 'success',
                    title: 'Peak Performance Window',
                    description: 'Your most productive hours are 9-11 AM. Consider scheduling deep work during this time.',
                    confidence: 95
                  },
                  {
                    type: 'warning',
                    title: 'Meeting Overload Alert',
                    description: 'Fridays have 40% more meetings than optimal. Try to reschedule some to other days.',
                    confidence: 87
                  },
                  {
                    type: 'info',
                    title: 'Break Pattern Analysis',
                    description: 'Taking a 15-minute break every 2 hours increases your afternoon productivity by 23%.',
                    confidence: 92
                  }
                ].map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-4 rounded-lg border ${
                      insight.type === 'success' ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800' :
                      insight.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800' :
                      'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
                    }`}
                  >
                    <h4 className="font-semibold text-sm mb-2">{insight.title}</h4>
                    <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className="text-xs">
                        {insight.confidence}% confidence
                      </Badge>
                      <Button size="sm" variant="ghost" className="text-xs h-6 px-2">
                        Apply
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-purple-500" />
                  <span>Recommendations</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  'Block 2-hour focus sessions in the morning',
                  'Limit meetings to 4 per day maximum',
                  'Schedule breaks every 90 minutes',
                  'Use "Do Not Disturb" during deep work',
                  'Review weekly goals every Monday'
                ].map((recommendation, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
                  >
                    <div className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs font-semibold text-purple-600 dark:text-purple-400">
                        {index + 1}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{recommendation}</p>
                      <div className="mt-2">
                        <Button size="sm" variant="outline" className="h-6 text-xs px-2 mr-2">
                          Apply Now
                        </Button>
                        <Button size="sm" variant="ghost" className="h-6 text-xs px-2">
                          Later
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  )
}