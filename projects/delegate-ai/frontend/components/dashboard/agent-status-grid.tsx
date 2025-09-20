"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Bot,
  Mail,
  Calendar,
  CheckSquare,
  Users,
  Activity,
  Zap,
  Cpu
} from "lucide-react"

interface Agent {
  id: string
  name: string
  type: 'communication' | 'calendar' | 'task' | 'collaboration' | 'analytics' | 'orchestrator'
  status: 'active' | 'idle' | 'processing' | 'offline'
  currentTask?: string
  completedTasks: number
  efficiency: number
  icon: React.ReactNode
  color: string
}

const agents: Agent[] = [
  {
    id: '1',
    name: 'Communication Agent',
    type: 'communication',
    status: 'processing',
    currentTask: 'Drafting client proposal response',
    completedTasks: 23,
    efficiency: 94,
    icon: <Mail className="w-4 h-4" />,
    color: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
  },
  {
    id: '2',
    name: 'Calendar Agent',
    type: 'calendar',
    status: 'active',
    currentTask: 'Analyzing schedule conflicts',
    completedTasks: 18,
    efficiency: 98,
    icon: <Calendar className="w-4 h-4" />,
    color: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
  },
  {
    id: '3',
    name: 'Task Manager',
    type: 'task',
    status: 'processing',
    currentTask: 'Breaking down project Alpha',
    completedTasks: 31,
    efficiency: 89,
    icon: <CheckSquare className="w-4 h-4" />,
    color: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
  },
  {
    id: '4',
    name: 'Collaboration Hub',
    type: 'collaboration',
    status: 'active',
    currentTask: 'Coordinating team sync',
    completedTasks: 12,
    efficiency: 96,
    icon: <Users className="w-4 h-4" />,
    color: 'bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300'
  },
  {
    id: '5',
    name: 'Analytics Engine',
    type: 'analytics',
    status: 'idle',
    currentTask: null,
    completedTasks: 8,
    efficiency: 92,
    icon: <Activity className="w-4 h-4" />,
    color: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
  },
  {
    id: '6',
    name: 'Orchestrator',
    type: 'orchestrator',
    status: 'active',
    currentTask: 'Managing agent workflows',
    completedTasks: 15,
    efficiency: 97,
    icon: <Cpu className="w-4 h-4" />,
    color: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
  }
]

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'active':
      return 'bg-green-500 text-white'
    case 'processing':
      return 'bg-blue-500 text-white animate-pulse'
    case 'idle':
      return 'bg-gray-500 text-white'
    case 'offline':
      return 'bg-red-500 text-white'
    default:
      return 'bg-gray-500 text-white'
  }
}

const getStatusText = (status: Agent['status']) => {
  switch (status) {
    case 'active':
      return 'Active'
    case 'processing':
      return 'Processing'
    case 'idle':
      return 'Idle'
    case 'offline':
      return 'Offline'
    default:
      return 'Unknown'
  }
}

export function AgentStatusGrid() {
  const activeAgents = agents.filter(agent => agent.status === 'active' || agent.status === 'processing').length
  const totalTasks = agents.reduce((sum, agent) => sum + agent.completedTasks, 0)
  const avgEfficiency = Math.round(agents.reduce((sum, agent) => sum + agent.efficiency, 0) / agents.length)

  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            AI Agent Status
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-muted-foreground">{activeAgents} Active</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-muted-foreground">{avgEfficiency}% Avg Efficiency</span>
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="relative p-4 rounded-lg border border-border bg-card hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <Avatar className={`w-10 h-10 ${agent.color}`}>
                    <AvatarFallback className={agent.color}>
                      {agent.icon}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-medium text-sm">{agent.name}</h4>
                    <Badge className={`text-xs ${getStatusColor(agent.status)}`}>
                      {getStatusText(agent.status)}
                    </Badge>
                  </div>
                </div>
              </div>

              {agent.currentTask && (
                <div className="mb-3">
                  <p className="text-xs text-muted-foreground font-medium mb-1">
                    Current Task:
                  </p>
                  <p className="text-xs text-foreground line-clamp-2">
                    {agent.currentTask}
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Efficiency</span>
                  <span className="font-medium">{agent.efficiency}%</span>
                </div>
                <Progress value={agent.efficiency} className="h-1" />

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-muted-foreground">Tasks Completed</span>
                  <span className="font-medium">{agent.completedTasks}</span>
                </div>
              </div>

              {/* Activity indicator */}
              {(agent.status === 'active' || agent.status === 'processing') && (
                <div className="absolute top-2 right-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="mt-6 pt-4 border-t border-border">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{totalTasks}</div>
              <div className="text-xs text-muted-foreground">Total Tasks</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{activeAgents}</div>
              <div className="text-xs text-muted-foreground">Active Agents</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{avgEfficiency}%</div>
              <div className="text-xs text-muted-foreground">Avg Efficiency</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}