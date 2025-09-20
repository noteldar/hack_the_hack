"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  Target,
  Zap,
  BarChart3,
  PieChart
} from "lucide-react"

interface Agent {
  id: string
  name: string
  type: 'communication' | 'calendar' | 'task' | 'collaboration' | 'analytics' | 'orchestrator'
  status: 'active' | 'idle' | 'processing' | 'offline' | 'error'
  currentTask?: string
  completedTasks: number
  efficiency: number
  uptime: number
  memoryUsage: number
  cpuUsage: number
  lastActivity: Date
  version: string
  capabilities: string[]
}

interface AgentPerformanceProps {
  agents: Agent[]
}

// Mock performance data for charts
const performanceData = {
  daily: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    efficiency: [85, 87, 92, 89, 94, 91, 88],
    tasks: [23, 31, 28, 35, 42, 38, 29],
    uptime: [98.2, 99.1, 97.8, 99.5, 99.8, 98.9, 99.2]
  },
  agents: {
    communication: { trend: 'up', change: 8, avgResponseTime: 45, satisfaction: 94 },
    calendar: { trend: 'up', change: 12, avgSchedulingTime: 15, conflicts: 2 },
    task: { trend: 'down', change: -3, avgBreakdownTime: 120, accuracy: 89 },
    collaboration: { trend: 'up', change: 15, avgCoordTime: 30, teamSatisfaction: 96 },
    analytics: { trend: 'up', change: 7, avgAnalysisTime: 180, insights: 234 },
    orchestrator: { trend: 'up', change: 5, loadBalancing: 97, efficiency: 95 }
  }
}

function PerformanceMetric({
  title,
  value,
  unit,
  trend,
  change,
  icon: Icon
}: {
  title: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down'
  change?: number
  icon: any
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">{title}</span>
          </div>
          {trend && change && (
            <div className={`flex items-center gap-1 ${
              trend === 'up' ? 'text-green-600' : 'text-red-600'
            }`}>
              {trend === 'up' ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span className="text-xs font-medium">
                {trend === 'up' ? '+' : ''}{change}%
              </span>
            </div>
          )}
        </div>
        <div className="mt-2">
          <span className="text-2xl font-bold">{value}</span>
          {unit && <span className="text-sm text-muted-foreground ml-1">{unit}</span>}
        </div>
      </CardContent>
    </Card>
  )
}

function AgentPerformanceCard({ agent, metrics }: { agent: Agent; metrics: any }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">{agent.name}</h3>
            <Badge variant="outline" className="mt-1">
              {agent.type}
            </Badge>
          </div>
          <div className={`flex items-center gap-1 ${
            metrics.trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {metrics.trend === 'up' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {metrics.trend === 'up' ? '+' : ''}{metrics.change}%
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Efficiency Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Efficiency</span>
            <span className="text-sm text-muted-foreground">{agent.efficiency}%</span>
          </div>
          <Progress value={agent.efficiency} className="h-2" />
        </div>

        {/* Agent-specific metrics */}
        <div className="grid grid-cols-2 gap-4">
          {agent.type === 'communication' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.avgResponseTime}s</div>
                <div className="text-xs text-muted-foreground">Avg Response</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.satisfaction}%</div>
                <div className="text-xs text-muted-foreground">Satisfaction</div>
              </div>
            </>
          )}
          {agent.type === 'calendar' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.avgSchedulingTime}s</div>
                <div className="text-xs text-muted-foreground">Scheduling Time</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.conflicts}</div>
                <div className="text-xs text-muted-foreground">Conflicts</div>
              </div>
            </>
          )}
          {agent.type === 'task' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.avgBreakdownTime}s</div>
                <div className="text-xs text-muted-foreground">Breakdown Time</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.accuracy}%</div>
                <div className="text-xs text-muted-foreground">Accuracy</div>
              </div>
            </>
          )}
          {agent.type === 'collaboration' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.avgCoordTime}s</div>
                <div className="text-xs text-muted-foreground">Coord Time</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.teamSatisfaction}%</div>
                <div className="text-xs text-muted-foreground">Team Rating</div>
              </div>
            </>
          )}
          {agent.type === 'analytics' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.avgAnalysisTime}s</div>
                <div className="text-xs text-muted-foreground">Analysis Time</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.insights}</div>
                <div className="text-xs text-muted-foreground">Insights Gen.</div>
              </div>
            </>
          )}
          {agent.type === 'orchestrator' && (
            <>
              <div>
                <div className="text-sm font-medium">{metrics.loadBalancing}%</div>
                <div className="text-xs text-muted-foreground">Load Balance</div>
              </div>
              <div>
                <div className="text-sm font-medium">{metrics.efficiency}%</div>
                <div className="text-xs text-muted-foreground">System Eff.</div>
              </div>
            </>
          )}
        </div>

        {/* Resource Usage */}
        <div className="pt-3 border-t border-border">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-muted-foreground">CPU:</span>{' '}
              <span className="font-medium">{agent.cpuUsage}%</span>
            </div>
            <div>
              <span className="text-muted-foreground">Memory:</span>{' '}
              <span className="font-medium">{agent.memoryUsage}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function AgentPerformance({ agents }: AgentPerformanceProps) {
  const totalTasks = agents.reduce((sum, agent) => sum + agent.completedTasks, 0)
  const avgEfficiency = Math.round(agents.reduce((sum, agent) => sum + agent.efficiency, 0) / agents.length)
  const avgUptime = Math.round(agents.reduce((sum, agent) => sum + agent.uptime, 0) / agents.length * 10) / 10
  const activeAgents = agents.filter(a => a.status === 'active' || a.status === 'processing').length

  return (
    <div className="space-y-6">
      {/* Overall Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <PerformanceMetric
          title="Total Tasks"
          value={totalTasks}
          trend="up"
          change={23}
          icon={Target}
        />
        <PerformanceMetric
          title="Avg Efficiency"
          value={avgEfficiency}
          unit="%"
          trend="up"
          change={5}
          icon={TrendingUp}
        />
        <PerformanceMetric
          title="System Uptime"
          value={avgUptime}
          unit="%"
          trend="up"
          change={2}
          icon={Clock}
        />
        <PerformanceMetric
          title="Active Agents"
          value={`${activeAgents}/${agents.length}`}
          trend="up"
          change={0}
          icon={Activity}
        />
      </div>

      {/* Performance Trends */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Weekly Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Efficiency Trend */}
            <div>
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Efficiency Trend
              </h4>
              <div className="space-y-2">
                {performanceData.daily.labels.map((day, index) => (
                  <div key={day} className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{day}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20">
                        <Progress value={performanceData.daily.efficiency[index]} className="h-1" />
                      </div>
                      <span className="text-sm font-medium w-8">
                        {performanceData.daily.efficiency[index]}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tasks Completed */}
            <div>
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Tasks Completed
              </h4>
              <div className="space-y-2">
                {performanceData.daily.labels.map((day, index) => (
                  <div key={day} className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{day}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20">
                        <Progress
                          value={(performanceData.daily.tasks[index] / 50) * 100}
                          className="h-1"
                        />
                      </div>
                      <span className="text-sm font-medium w-8">
                        {performanceData.daily.tasks[index]}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Uptime */}
            <div>
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                System Uptime
              </h4>
              <div className="space-y-2">
                {performanceData.daily.labels.map((day, index) => (
                  <div key={day} className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{day}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20">
                        <Progress value={performanceData.daily.uptime[index]} className="h-1" />
                      </div>
                      <span className="text-sm font-medium w-12">
                        {performanceData.daily.uptime[index]}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Agent Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-5 h-5" />
            Individual Agent Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <AgentPerformanceCard
                key={agent.id}
                agent={agent}
                metrics={performanceData.agents[agent.type] || { trend: 'up', change: 0 }}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Insights */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
            <Zap className="w-5 h-5" />
            Performance Insights
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <p className="text-sm">
                  <strong>Communication Agent</strong> shows 8% improvement in response times this week
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                <p className="text-sm">
                  <strong>Calendar Agent</strong> reduced scheduling conflicts by 60% with better optimization
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2" />
                <p className="text-sm">
                  <strong>Analytics Engine</strong> generated 234 actionable insights this week
                </p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2" />
                <p className="text-sm">
                  <strong>System Recommendation:</strong> Consider load balancing during peak hours (9-11 AM)
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-pink-500 rounded-full mt-2" />
                <p className="text-sm">
                  <strong>Resource Usage:</strong> Memory optimization could improve overall performance by 12%
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}