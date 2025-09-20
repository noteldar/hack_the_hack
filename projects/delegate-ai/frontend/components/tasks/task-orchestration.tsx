"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TaskFlow } from "./task-flow"
import { TaskQueue } from "./task-queue"
import { TaskMatrix } from "./task-matrix"
import {
  CheckSquare,
  Plus,
  Bot,
  Zap,
  Clock,
  Target,
  TrendingUp,
  Activity
} from "lucide-react"

interface Task {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'blocked'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignedAgent?: string
  dependencies: string[]
  subtasks: Task[]
  estimatedTime: number
  actualTime?: number
  createdAt: Date
  dueDate?: Date
  tags: string[]
  aiGenerated: boolean
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Launch Marketing Campaign',
    description: 'Plan and execute Q4 marketing campaign for new product line',
    status: 'in_progress',
    priority: 'high',
    assignedAgent: 'Task Manager',
    dependencies: [],
    estimatedTime: 480, // 8 hours
    actualTime: 120, // 2 hours so far
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
    tags: ['marketing', 'product', 'campaign'],
    aiGenerated: true,
    subtasks: [
      {
        id: '1a',
        title: 'Market Research Analysis',
        description: 'Analyze competitor campaigns and market trends',
        status: 'completed',
        priority: 'high',
        assignedAgent: 'Analytics Engine',
        dependencies: [],
        estimatedTime: 60,
        actualTime: 55,
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        tags: ['research', 'analysis'],
        aiGenerated: true,
        subtasks: []
      },
      {
        id: '1b',
        title: 'Create Campaign Materials',
        description: 'Design graphics, write copy, and create video content',
        status: 'in_progress',
        priority: 'high',
        assignedAgent: 'Creative Agent',
        dependencies: ['1a'],
        estimatedTime: 180,
        actualTime: 65,
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        tags: ['creative', 'design'],
        aiGenerated: true,
        subtasks: []
      },
      {
        id: '1c',
        title: 'Set up Analytics Tracking',
        description: 'Configure campaign tracking and KPI monitoring',
        status: 'pending',
        priority: 'medium',
        dependencies: ['1b'],
        estimatedTime: 90,
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        tags: ['analytics', 'tracking'],
        aiGenerated: true,
        subtasks: []
      }
    ]
  },
  {
    id: '2',
    title: 'Client Proposal - TechCorp',
    description: 'Prepare comprehensive proposal for TechCorp engagement',
    status: 'pending',
    priority: 'urgent',
    assignedAgent: 'Communication Agent',
    dependencies: [],
    estimatedTime: 240, // 4 hours
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    tags: ['client', 'proposal', 'sales'],
    aiGenerated: false,
    subtasks: []
  },
  {
    id: '3',
    title: 'System Performance Optimization',
    description: 'Optimize system performance and reduce load times',
    status: 'in_progress',
    priority: 'medium',
    assignedAgent: 'Technical Agent',
    dependencies: [],
    estimatedTime: 360, // 6 hours
    actualTime: 180, // 3 hours so far
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    tags: ['technical', 'optimization'],
    aiGenerated: true,
    subtasks: []
  }
]

export function TaskOrchestration() {
  const totalTasks = mockTasks.reduce((sum, task) => sum + task.subtasks.length + 1, 0)
  const completedTasks = mockTasks.reduce((sum, task) => {
    const mainCompleted = task.status === 'completed' ? 1 : 0
    const subCompleted = task.subtasks.filter(st => st.status === 'completed').length
    return sum + mainCompleted + subCompleted
  }, 0)
  const inProgressTasks = mockTasks.reduce((sum, task) => {
    const mainInProgress = task.status === 'in_progress' ? 1 : 0
    const subInProgress = task.subtasks.filter(st => st.status === 'in_progress').length
    return sum + mainInProgress + subInProgress
  }, 0)
  const blockedTasks = mockTasks.reduce((sum, task) => {
    const mainBlocked = task.status === 'blocked' ? 1 : 0
    const subBlocked = task.subtasks.filter(st => st.status === 'blocked').length
    return sum + mainBlocked + subBlocked
  }, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Task Orchestration</h1>
          <p className="text-muted-foreground mt-1">
            AI-powered task breakdown and autonomous execution
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Task
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Tasks</p>
                <p className="text-2xl font-bold">{totalTasks}</p>
              </div>
              <CheckSquare className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">In Progress</p>
                <p className="text-2xl font-bold text-yellow-600">{inProgressTasks}</p>
              </div>
              <Activity className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-green-600">{completedTasks}</p>
              </div>
              <Target className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Blocked</p>
                <p className="text-2xl font-bold text-red-600">{blockedTasks}</p>
              </div>
              <Clock className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Orchestration Banner */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold text-purple-900 dark:text-purple-100">
                  AI Task Orchestrator Active
                </h3>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  Automatically breaking down complex tasks • Optimizing execution order
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">23% faster</span>
                </div>
                <p className="text-xs text-muted-foreground">completion rate</p>
              </div>
              <Button variant="secondary" size="sm" className="bg-white/50 hover:bg-white/70">
                <Zap className="w-4 h-4 mr-2" />
                Optimize
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="flow" className="space-y-6">
        <TabsList>
          <TabsTrigger value="flow">Task Flow</TabsTrigger>
          <TabsTrigger value="queue">Queue</TabsTrigger>
          <TabsTrigger value="matrix">Priority Matrix</TabsTrigger>
        </TabsList>

        <TabsContent value="flow">
          <TaskFlow tasks={mockTasks} />
        </TabsContent>

        <TabsContent value="queue">
          <TaskQueue tasks={mockTasks} />
        </TabsContent>

        <TabsContent value="matrix">
          <TaskMatrix tasks={mockTasks} />
        </TabsContent>
      </Tabs>
    </div>
  )
}