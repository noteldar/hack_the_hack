"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { formatTime } from "@/lib/utils"
import {
  Bot,
  Play,
  Pause,
  RefreshCw,
  Settings,
  Activity,
  Cpu,
  MemoryStick,
  Clock,
  CheckCircle,
  AlertCircle,
  PlayCircle,
  StopCircle
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

interface AgentStatusGridProps {
  agents: Agent[]
}

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'active':
      return 'bg-green-500 text-white'
    case 'processing':
      return 'bg-blue-500 text-white animate-pulse'
    case 'idle':
      return 'bg-yellow-500 text-white'
    case 'offline':
      return 'bg-gray-500 text-white'
    case 'error':
      return 'bg-red-500 text-white'
    default:
      return 'bg-gray-500 text-white'
  }
}

const getStatusIcon = (status: Agent['status']) => {
  switch (status) {
    case 'active':
      return <CheckCircle className="w-4 h-4" />
    case 'processing':
      return <PlayCircle className="w-4 h-4" />
    case 'idle':
      return <Clock className="w-4 h-4" />
    case 'offline':
      return <StopCircle className="w-4 h-4" />
    case 'error':
      return <AlertCircle className="w-4 h-4" />
    default:
      return <Bot className="w-4 h-4" />
  }
}

const getTypeColor = (type: Agent['type']) => {
  switch (type) {
    case 'communication':
      return 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
    case 'calendar':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
    case 'task':
      return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
    case 'collaboration':
      return 'bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300'
    case 'analytics':
      return 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
    case 'orchestrator':
      return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
  }
}

function AgentCard({ agent }: { agent: Agent }) {
  return (
    <Card className="relative overflow-hidden transition-all hover:shadow-lg">
      {/* Status indicator */}
      <div className="absolute top-3 right-3">
        <div className={`w-3 h-3 rounded-full ${
          agent.status === 'active' || agent.status === 'processing' ? 'animate-pulse' : ''
        } ${
          agent.status === 'active' || agent.status === 'processing' ? 'bg-green-500' :
          agent.status === 'idle' ? 'bg-yellow-500' :
          agent.status === 'error' ? 'bg-red-500' :
          'bg-gray-500'
        }`} />
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar className={`w-12 h-12 ${getTypeColor(agent.type)}`}>
              <AvatarFallback className={getTypeColor(agent.type)}>
                <Bot className="w-6 h-6" />
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold">{agent.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className={getTypeColor(agent.type)}>
                  {agent.type}
                </Badge>
                <Badge className={`text-xs ${getStatusColor(agent.status)}`}>
                  {getStatusIcon(agent.status)}
                  <span className="ml-1 capitalize">{agent.status}</span>
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current Activity */}
        {agent.currentTask && (
          <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
              Current Task
            </h4>
            <p className="text-sm text-blue-700 dark:text-blue-300 line-clamp-2">
              {agent.currentTask}
            </p>
          </div>
        )}

        {/* Performance Metrics */}
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">Efficiency</span>
              <span className="text-sm text-muted-foreground">{agent.efficiency}%</span>
            </div>
            <Progress value={agent.efficiency} className="h-2" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="flex items-center gap-1 mb-1">
                <Cpu className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">CPU</span>
              </div>
              <div className="text-sm font-medium">{agent.cpuUsage}%</div>
            </div>
            <div>
              <div className="flex items-center gap-1 mb-1">
                <MemoryStick className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Memory</span>
              </div>
              <div className="text-sm font-medium">{agent.memoryUsage}%</div>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4 pt-3 border-t border-border">
          <div>
            <div className="text-sm font-semibold text-primary">{agent.completedTasks}</div>
            <div className="text-xs text-muted-foreground">Tasks Done</div>
          </div>
          <div>
            <div className="text-sm font-semibold text-green-600">{agent.uptime}%</div>
            <div className="text-xs text-muted-foreground">Uptime</div>
          </div>
        </div>

        {/* Last Activity */}
        <div className="text-xs text-muted-foreground">
          Last active: {formatTime(agent.lastActivity)}
        </div>

        {/* Capabilities */}
        <div className="space-y-2">
          <h5 className="text-xs font-medium text-muted-foreground uppercase">Capabilities</h5>
          <div className="flex flex-wrap gap-1">
            {agent.capabilities.slice(0, 3).map((capability) => (
              <Badge key={capability} variant="secondary" className="text-xs">
                {capability}
              </Badge>
            ))}
            {agent.capabilities.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{agent.capabilities.length - 3}
              </Badge>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t border-border">
          {agent.status === 'active' || agent.status === 'processing' ? (
            <Button variant="outline" size="sm" className="flex-1">
              <Pause className="w-4 h-4 mr-2" />
              Pause
            </Button>
          ) : agent.status === 'idle' ? (
            <Button variant="outline" size="sm" className="flex-1">
              <Play className="w-4 h-4 mr-2" />
              Activate
            </Button>
          ) : (
            <Button variant="outline" size="sm" className="flex-1">
              <RefreshCw className="w-4 h-4 mr-2" />
              Restart
            </Button>
          )}
          <Button variant="ghost" size="icon">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export function AgentStatusGrid({ agents }: AgentStatusGridProps) {
  return (
    <div className="space-y-6">
      {/* Grid Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Agent Status Grid
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh All
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Batch Configure
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="justify-start">
              <Play className="w-4 h-4 mr-2" />
              Start All Idle Agents
            </Button>
            <Button variant="outline" className="justify-start">
              <RefreshCw className="w-4 h-4 mr-2" />
              Restart Error Agents
            </Button>
            <Button variant="outline" className="justify-start">
              <Settings className="w-4 h-4 mr-2" />
              Update All Agents
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}