"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { formatTime, getTimeAgo } from "@/lib/utils"
import {
  Activity,
  Search,
  Filter,
  Bot,
  CheckCircle,
  AlertCircle,
  Clock,
  Info,
  AlertTriangle,
  Download,
  RefreshCw
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

interface LogEntry {
  id: string
  timestamp: Date
  level: 'info' | 'warning' | 'error' | 'success'
  agentId: string
  agentName: string
  event: string
  description: string
  details?: any
  duration?: number
}

interface AgentLogsProps {
  agents: Agent[]
}

const mockLogEntries: LogEntry[] = [
  {
    id: '1',
    timestamp: new Date(Date.now() - 30 * 1000),
    level: 'success',
    agentId: '1',
    agentName: 'Communication Agent',
    event: 'Email Response Generated',
    description: 'Successfully generated response for client inquiry',
    details: { subject: 'Q4 Budget Review', confidence: 92 },
    duration: 45
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    level: 'info',
    agentId: '2',
    agentName: 'Calendar Agent',
    event: 'Schedule Optimization',
    description: 'Optimized weekly schedule, resolved 2 conflicts',
    details: { conflicts_resolved: 2, time_saved: '45min' },
    duration: 120
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    level: 'warning',
    agentId: '3',
    agentName: 'Task Manager',
    event: 'High Memory Usage',
    description: 'Memory usage exceeded 75% threshold',
    details: { memory_usage: '76%', threshold: '75%' }
  },
  {
    id: '4',
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    level: 'success',
    agentId: '4',
    agentName: 'Collaboration Hub',
    event: 'Team Coordination',
    description: 'Successfully coordinated cross-team meeting',
    details: { teams: ['Engineering', 'Product', 'Design'], attendees: 12 },
    duration: 180
  },
  {
    id: '5',
    timestamp: new Date(Date.now() - 12 * 60 * 1000),
    level: 'info',
    agentId: '1',
    agentName: 'Communication Agent',
    event: 'Email Processed',
    description: 'Categorized and prioritized incoming email',
    details: { category: 'client', priority: 'high' },
    duration: 15
  },
  {
    id: '6',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    level: 'error',
    agentId: '5',
    agentName: 'Analytics Engine',
    event: 'Data Processing Failed',
    description: 'Failed to process analytics data due to API timeout',
    details: { error_code: 'TIMEOUT', api: 'analytics-service' }
  },
  {
    id: '7',
    timestamp: new Date(Date.now() - 18 * 60 * 1000),
    level: 'success',
    agentId: '6',
    agentName: 'Orchestrator',
    event: 'Load Balancing',
    description: 'Redistributed tasks across agents for optimal performance',
    details: { tasks_moved: 3, efficiency_gain: '12%' },
    duration: 60
  },
  {
    id: '8',
    timestamp: new Date(Date.now() - 22 * 60 * 1000),
    level: 'info',
    agentId: '3',
    agentName: 'Task Manager',
    event: 'Task Breakdown',
    description: 'Broke down complex project into 12 subtasks',
    details: { parent_task: 'Marketing Campaign', subtasks: 12 },
    duration: 240
  },
  {
    id: '9',
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    level: 'warning',
    agentId: '2',
    agentName: 'Calendar Agent',
    event: 'Scheduling Conflict',
    description: 'Detected potential scheduling conflict for CEO',
    details: { meeting1: 'Board Meeting', meeting2: 'Client Call', overlap: '15min' }
  },
  {
    id: '10',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    level: 'success',
    agentId: '1',
    agentName: 'Communication Agent',
    event: 'Auto-Reply Sent',
    description: 'Sent automated response to routine inquiry',
    details: { recipient: 'vendor@company.com', template: 'payment_confirmation' },
    duration: 8
  }
]

const getLevelColor = (level: LogEntry['level']) => {
  switch (level) {
    case 'success':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'info':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
    case 'error':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
  }
}

const getLevelIcon = (level: LogEntry['level']) => {
  switch (level) {
    case 'success':
      return <CheckCircle className="w-4 h-4" />
    case 'info':
      return <Info className="w-4 h-4" />
    case 'warning':
      return <AlertTriangle className="w-4 h-4" />
    case 'error':
      return <AlertCircle className="w-4 h-4" />
  }
}

function LogEntryCard({ entry }: { entry: LogEntry }) {
  return (
    <Card className="mb-3 transition-all hover:shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Agent Avatar */}
          <Avatar className="w-8 h-8">
            <AvatarFallback className="bg-blue-100 text-blue-700">
              <Bot className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>

          {/* Log Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={getLevelColor(entry.level)}>
                  {getLevelIcon(entry.level)}
                  <span className="ml-1 capitalize">{entry.level}</span>
                </Badge>
                <span className="text-sm font-medium">{entry.agentName}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatTime(entry.timestamp)}</span>
                <span>•</span>
                <span>{getTimeAgo(entry.timestamp)}</span>
              </div>
            </div>

            <h4 className="font-medium text-sm mb-1">{entry.event}</h4>
            <p className="text-sm text-muted-foreground mb-2">{entry.description}</p>

            {/* Details */}
            {entry.details && (
              <div className="p-2 bg-muted/30 rounded text-xs">
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(entry.details).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-muted-foreground capitalize">
                        {key.replace('_', ' ')}:
                      </span>
                      <span className="font-mono">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Duration */}
            {entry.duration && (
              <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span>Completed in {entry.duration}s</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function AgentLogs({ agents }: AgentLogsProps) {
  const logStats = {
    success: mockLogEntries.filter(log => log.level === 'success').length,
    info: mockLogEntries.filter(log => log.level === 'info').length,
    warning: mockLogEntries.filter(log => log.level === 'warning').length,
    error: mockLogEntries.filter(log => log.level === 'error').length
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Activity Logs */}
      <div className="lg:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Agent Activity Logs
                <Badge variant="secondary">Live</Badge>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search logs..."
                    className="pl-10 w-64"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-0 max-h-96 overflow-y-auto">
              {mockLogEntries.map((entry) => (
                <LogEntryCard key={entry.id} entry={entry} />
              ))}
            </div>

            {/* Load More */}
            <div className="flex justify-center pt-4 border-t border-border">
              <Button variant="outline" size="sm">
                Load More Logs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* Log Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Log Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm">Success</span>
              </div>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                {logStats.success}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span className="text-sm">Info</span>
              </div>
              <Badge variant="outline" className="bg-blue-100 text-blue-800">
                {logStats.info}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-500" />
                <span className="text-sm">Warning</span>
              </div>
              <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                {logStats.warning}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span className="text-sm">Error</span>
              </div>
              <Badge variant="outline" className="bg-red-100 text-red-800">
                {logStats.error}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Agent Filter */}
        <Card>
          <CardHeader>
            <CardTitle>Filter by Agent</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start" size="sm">
              All Agents
            </Button>
            {agents.map((agent) => {
              const agentLogs = mockLogEntries.filter(log => log.agentId === agent.id).length
              return (
                <div key={agent.id} className="flex items-center justify-between">
                  <span className="text-sm truncate">{agent.name}</span>
                  <Badge variant="secondary">{agentLogs}</Badge>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Export Options */}
        <Card>
          <CardHeader>
            <CardTitle>Export Logs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export as CSV
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export as JSON
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Generate Report
            </Button>
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card className="bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <AlertTriangle className="w-5 h-5" />
              Recent Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {mockLogEntries
              .filter(log => log.level === 'error' || log.level === 'warning')
              .slice(0, 3)
              .map((alert) => (
                <div key={alert.id} className="p-2 bg-white/50 rounded text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    {getLevelIcon(alert.level)}
                    <span className="font-medium">{alert.agentName}</span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {alert.description}
                  </p>
                  <div className="text-xs text-muted-foreground mt-1">
                    {getTimeAgo(alert.timestamp)}
                  </div>
                </div>
              ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}