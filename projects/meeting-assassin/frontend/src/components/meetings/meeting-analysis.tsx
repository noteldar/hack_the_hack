'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  Users,
  Clock,
  TrendingUp,
  MessageSquare,
  Target,
  AlertCircle,
  CheckCircle2,
  Calendar,
  PlayCircle
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const recentMeetings = [
  {
    id: '1',
    title: 'Weekly Team Standup',
    date: '2024-01-15',
    duration: 30,
    attendees: 8,
    efficiency: 92,
    engagement: 87,
    outcomes: 5,
    status: 'analyzed',
    insights: {
      timeWasted: 5,
      productiveTime: 25,
      recommendations: [
        'Reduce status updates to 1 minute per person',
        'Move detailed discussions to separate meetings',
        'Use async updates for non-critical items'
      ]
    }
  },
  {
    id: '2',
    title: 'Product Strategy Session',
    date: '2024-01-14',
    duration: 90,
    attendees: 6,
    efficiency: 78,
    engagement: 94,
    outcomes: 8,
    status: 'analyzed',
    insights: {
      timeWasted: 18,
      productiveTime: 72,
      recommendations: [
        'Prepare agenda with time allocations',
        'Assign action items during meeting',
        'Follow up with summary within 24 hours'
      ]
    }
  },
  {
    id: '3',
    title: 'Client Presentation Prep',
    date: '2024-01-13',
    duration: 45,
    attendees: 4,
    efficiency: 85,
    engagement: 91,
    outcomes: 6,
    status: 'processing',
    insights: {
      timeWasted: 7,
      productiveTime: 38,
      recommendations: []
    }
  }
]

const meetingTrends = [
  { month: 'Oct', efficiency: 78, count: 42, avgDuration: 52 },
  { month: 'Nov', efficiency: 82, count: 38, avgDuration: 48 },
  { month: 'Dec', efficiency: 85, count: 35, avgDuration: 45 },
  { month: 'Jan', efficiency: 88, count: 32, avgDuration: 42 }
]

const meetingTypes = [
  { name: 'Standup', value: 35, color: '#8b5cf6' },
  { name: 'Strategy', value: 25, color: '#3b82f6' },
  { name: 'Client', value: 20, color: '#10b981' },
  { name: 'Planning', value: 15, color: '#f59e0b' },
  { name: 'Review', value: 5, color: '#ef4444' }
]

export function MeetingAnalysis() {
  const [selectedMeeting, setSelectedMeeting] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Meeting Analysis
          </h1>
          <p className="text-muted-foreground mt-2">
            AI-powered insights into your meeting effectiveness
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button className="bg-gradient-to-r from-purple-500 to-blue-600 text-white">
            <PlayCircle className="w-4 h-4 mr-2" />
            Analyze New Meeting
          </Button>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            title: 'Average Efficiency',
            value: '88%',
            change: '+6%',
            icon: Target,
            color: 'from-green-500 to-emerald-500'
          },
          {
            title: 'Meetings This Month',
            value: '32',
            change: '-9%',
            icon: Calendar,
            color: 'from-blue-500 to-cyan-500'
          },
          {
            title: 'Time Saved',
            value: '4.2h',
            change: '+12%',
            icon: Clock,
            color: 'from-purple-500 to-pink-500'
          },
          {
            title: 'Action Items',
            value: '156',
            change: '+18%',
            icon: CheckCircle2,
            color: 'from-orange-500 to-red-500'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="glass-card glow-effect">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                  <Badge variant={stat.change.startsWith('+') ? 'default' : 'destructive'}>
                    {stat.change}
                  </Badge>
                </div>
                <div>
                  <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Tabs defaultValue="recent" className="space-y-4">
        <TabsList>
          <TabsTrigger value="recent">Recent Meetings</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="recent" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Meeting List */}
            <div className="lg:col-span-2">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-purple-500" />
                    <span>Recent Meetings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recentMeetings.map((meeting, index) => (
                    <motion.div
                      key={meeting.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedMeeting === meeting.id
                          ? 'bg-purple-50 dark:bg-purple-950/20 border-purple-500/50'
                          : 'bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => setSelectedMeeting(
                        selectedMeeting === meeting.id ? null : meeting.id
                      )}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">{meeting.title}</h3>
                        <Badge
                          variant={meeting.status === 'analyzed' ? 'default' : 'secondary'}
                        >
                          {meeting.status}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div className="text-center">
                          <div className="text-lg font-bold">{meeting.efficiency}%</div>
                          <div className="text-xs text-muted-foreground">Efficiency</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold">{meeting.duration}m</div>
                          <div className="text-xs text-muted-foreground">Duration</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold">{meeting.attendees}</div>
                          <div className="text-xs text-muted-foreground">Attendees</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold">{meeting.outcomes}</div>
                          <div className="text-xs text-muted-foreground">Outcomes</div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Efficiency Score</span>
                          <span>{meeting.efficiency}%</span>
                        </div>
                        <Progress value={meeting.efficiency} className="h-2" />
                      </div>

                      {selectedMeeting === meeting.id && meeting.status === 'analyzed' && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-4 pt-4 border-t"
                        >
                          <h4 className="font-semibold mb-2">AI Recommendations</h4>
                          <ul className="space-y-1">
                            {meeting.insights.recommendations.map((rec, i) => (
                              <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                                <CheckCircle2 className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Meeting Types */}
            <div>
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="w-5 h-5 text-blue-500" />
                    <span>Meeting Types</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        dataKey="value"
                        data={meetingTypes}
                        cx="50%"
                        cy="50%"
                        outerRadius={60}
                        innerRadius={30}
                        paddingAngle={5}
                      >
                        {meetingTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2 mt-4">
                    {meetingTypes.map((type, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: type.color }}
                          />
                          <span className="text-sm">{type.name}</span>
                        </div>
                        <span className="text-sm font-medium">{type.value}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                <span>Meeting Efficiency Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={meetingTrends}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="efficiency"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ fill: '#8b5cf6', r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Top Insights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  {
                    type: 'success',
                    title: 'Meeting Duration Optimized',
                    description: 'Average meeting length decreased by 23% this month'
                  },
                  {
                    type: 'warning',
                    title: 'Engagement Opportunity',
                    description: 'Strategy meetings show 15% lower engagement than optimal'
                  },
                  {
                    type: 'info',
                    title: 'Best Practice Identified',
                    description: 'Meetings with agendas are 34% more efficient'
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
                    <p className="text-sm text-muted-foreground">{insight.description}</p>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  'Implement 25-minute default meeting duration',
                  'Require agenda 24 hours before meeting',
                  'Limit meeting size to 8 people maximum',
                  'Use async communication for status updates'
                ].map((rec, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
                  >
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{rec}</span>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}