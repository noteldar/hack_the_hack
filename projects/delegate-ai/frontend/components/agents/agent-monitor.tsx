"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AgentStatusGrid } from "./agent-status-grid"
import { AgentPerformance } from "./agent-performance"
import { AgentLogs } from "./agent-logs"
import {
  Bot,
  Activity,
  Zap,
  Settings,
  Play,
  Pause,
  RefreshCw,
  TrendingUp,
  Cpu,
  Database
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

const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Communication Agent',
    type: 'communication',
    status: 'processing',
    currentTask: 'Drafting client proposal response',
    completedTasks: 127,
    efficiency: 94,
    uptime: 99.8,
    memoryUsage: 68,
    cpuUsage: 34,
    lastActivity: new Date(Date.now() - 30 * 1000),
    version: '2.1.4',
    capabilities: ['Email Processing', 'Response Generation', 'Sentiment Analysis', 'Language Translation']
  },
  {
    id: '2',
    name: 'Calendar Agent',
    type: 'calendar',
    status: 'active',
    currentTask: 'Optimizing weekly schedule',
    completedTasks: 89,
    efficiency: 98,
    uptime: 100,
    memoryUsage: 42,
    cpuUsage: 18,
    lastActivity: new Date(Date.now() - 45 * 1000),
    version: '1.8.2',
    capabilities: ['Schedule Management', 'Meeting Coordination', 'Conflict Resolution', 'Time Optimization']
  },
  {
    id: '3',
    name: 'Task Manager',
    type: 'task',
    status: 'processing',
    currentTask: 'Breaking down marketing campaign project',
    completedTasks: 156,
    efficiency: 89,
    uptime: 97.2,
    memoryUsage: 73,
    cpuUsage: 56,
    lastActivity: new Date(Date.now() - 12 * 1000),
    version: '3.0.1',
    capabilities: ['Task Breakdown', 'Priority Analysis', 'Dependency Mapping', 'Resource Allocation']
  },
  {
    id: '4',
    name: 'Collaboration Hub',
    type: 'collaboration',
    status: 'active',
    currentTask: 'Coordinating cross-team communication',
    completedTasks: 67,
    efficiency: 96,
    uptime: 99.1,
    memoryUsage: 51,
    cpuUsage: 23,
    lastActivity: new Date(Date.now() - 67 * 1000),
    version: '1.5.3',
    capabilities: ['Team Coordination', 'Information Sharing', 'Status Updates', 'Workflow Integration']
  },
  {
    id: '5',
    name: 'Analytics Engine',
    type: 'analytics',
    status: 'idle',
    currentTask: null,
    completedTasks: 234,
    efficiency: 92,
    uptime: 96.8,
    memoryUsage: 39,
    cpuUsage: 8,
    lastActivity: new Date(Date.now() - 5 * 60 * 1000),
    version: '2.3.0',
    capabilities: ['Data Analysis', 'Pattern Recognition', 'Reporting', 'Predictive Insights']
  },
  {
    id: '6',
    name: 'Orchestrator',
    type: 'orchestrator',
    status: 'active',
    currentTask: 'Managing agent workflows and priorities',
    completedTasks: 45,
    efficiency: 97,
    uptime: 99.9,
    memoryUsage: 34,
    cpuUsage: 15,
    lastActivity: new Date(Date.now() - 8 * 1000),
    version: '1.2.1',
    capabilities: ['Agent Coordination', 'Task Distribution', 'Load Balancing', 'System Optimization']
  }
]

export function AgentMonitor() {
  const activeAgents = mockAgents.filter(agent =>
    agent.status === 'active' || agent.status === 'processing'
  ).length

  const totalTasks = mockAgents.reduce((sum, agent) => sum + agent.completedTasks, 0)
  const avgEfficiency = Math.round(mockAgents.reduce((sum, agent) => sum + agent.efficiency, 0) / mockAgents.length)
  const avgUptime = Math.round(mockAgents.reduce((sum, agent) => sum + agent.uptime, 0) / mockAgents.length * 10) / 10

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Monitor</h1>
          <p className="text-muted-foreground mt-1">
            Real-time monitoring and management of AI agents
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4 mr-2" />
            Configure
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Agents</p>
                <p className="text-2xl font-bold text-green-600">{activeAgents}</p>
                <p className="text-xs text-muted-foreground">of {mockAgents.length} total</p>
              </div>
              <Bot className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tasks Completed</p>
                <p className="text-2xl font-bold">{totalTasks}</p>
                <p className="text-xs text-green-600">+23% today</p>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Efficiency</p>
                <p className="text-2xl font-bold">{avgEfficiency}%</p>
                <p className="text-xs text-green-600">+5% this week</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">System Uptime</p>
                <p className="text-2xl font-bold">{avgUptime}%</p>
                <p className="text-xs text-muted-foreground">last 30 days</p>
              </div>
              <Cpu className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Status Banner */}
      <Card className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-green-200 dark:border-green-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold text-green-900 dark:text-green-100">
                  All Systems Operational
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  {activeAgents} agents active • Processing {mockAgents.filter(a => a.status === 'processing').length} tasks • No critical alerts
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-green-600">Healthy</span>
                </div>
                <p className="text-xs text-muted-foreground">System status</p>
              </div>
              <Button variant="secondary" size="sm" className="bg-white/50 hover:bg-white/70">
                <Zap className="w-4 h-4 mr-2" />
                Optimize
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-5 h-5" />
              System Resources
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">CPU Usage</span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(mockAgents.reduce((sum, agent) => sum + agent.cpuUsage, 0) / mockAgents.length)}%
                </span>
              </div>
              <Progress
                value={mockAgents.reduce((sum, agent) => sum + agent.cpuUsage, 0) / mockAgents.length}
                className="h-2"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Memory Usage</span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(mockAgents.reduce((sum, agent) => sum + agent.memoryUsage, 0) / mockAgents.length)}%
                </span>
              </div>
              <Progress
                value={mockAgents.reduce((sum, agent) => sum + agent.memoryUsage, 0) / mockAgents.length}
                className="h-2"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Network I/O</span>
                <span className="text-sm text-muted-foreground">Normal</span>
              </div>
              <Progress value={42} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Agent Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {['communication', 'task', 'calendar', 'analytics', 'collaboration', 'orchestrator'].map((type) => {
                const agents = mockAgents.filter(a => a.type === type)
                const activeCount = agents.filter(a => a.status === 'active' || a.status === 'processing').length

                return (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{type}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        {activeCount}/{agents.length}
                      </span>
                      <div className="flex items-center gap-1">
                        {agents.map((agent, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${
                              agent.status === 'active' || agent.status === 'processing'
                                ? 'bg-green-500'
                                : agent.status === 'idle'
                                ? 'bg-yellow-500'
                                : 'bg-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="grid" className="space-y-6">
        <TabsList>
          <TabsTrigger value="grid">Agent Grid</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="logs">Activity Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="grid">
          <AgentStatusGrid agents={mockAgents} />
        </TabsContent>

        <TabsContent value="performance">
          <AgentPerformance agents={mockAgents} />
        </TabsContent>

        <TabsContent value="logs">
          <AgentLogs agents={mockAgents} />
        </TabsContent>
      </Tabs>
    </div>
  )
}