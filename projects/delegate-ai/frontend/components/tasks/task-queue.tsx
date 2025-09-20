"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  CheckCircle,
  Clock,
  Play,
  AlertTriangle,
  Bot,
  ArrowUp,
  ArrowDown,
  Pause,
  MoreHorizontal
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

interface TaskQueueProps {
  tasks: Task[]
}

const getStatusIcon = (status: Task['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'in_progress':
      return <Play className="w-4 h-4 text-blue-500" />
    case 'blocked':
      return <AlertTriangle className="w-4 h-4 text-red-500" />
    case 'pending':
      return <Clock className="w-4 h-4 text-gray-500" />
  }
}

const getPriorityColor = (priority: Task['priority']) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100 border-red-200'
    case 'high':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100 border-orange-200'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100 border-yellow-200'
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 border-green-200'
  }
}

const getProgressPercentage = (task: Task) => {
  if (task.status === 'completed') return 100
  if (task.status === 'pending') return 0
  if (task.actualTime && task.estimatedTime) {
    return Math.min((task.actualTime / task.estimatedTime) * 100, 100)
  }
  return 25
}

function QueuedTaskCard({ task, position }: { task: Task; position: number }) {
  const progress = getProgressPercentage(task)
  const allSubtasks = task.subtasks || []

  return (
    <Card className={`mb-3 transition-all hover:shadow-sm border-l-4 ${
      task.status === 'in_progress' ? 'border-l-blue-500 bg-blue-50/30 dark:bg-blue-950/10' :
      task.status === 'blocked' ? 'border-l-red-500 bg-red-50/30 dark:bg-red-950/10' :
      task.priority === 'urgent' ? 'border-l-red-400' :
      task.priority === 'high' ? 'border-l-orange-400' :
      'border-l-gray-300'
    }`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center text-sm font-medium">
                {position + 1}
              </div>
              {getStatusIcon(task.status)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-medium truncate">{task.title}</h4>
                <Badge variant="outline" className={`text-xs ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </Badge>
                {task.aiGenerated && (
                  <Badge variant="outline" className="bg-purple-50 text-purple-700 text-xs">
                    <Bot className="w-3 h-3 mr-1" />
                    AI
                  </Badge>
                )}
              </div>

              <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                {task.description}
              </p>

              <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground mb-3">
                <div>
                  <span className="font-medium">Estimated:</span> {Math.round(task.estimatedTime / 60)}h
                </div>
                {task.actualTime && (
                  <div>
                    <span className="font-medium">Actual:</span> {Math.round(task.actualTime / 60)}h
                  </div>
                )}
                {task.dueDate && (
                  <div>
                    <span className="font-medium">Due:</span> {task.dueDate.toLocaleDateString()}
                  </div>
                )}
                {allSubtasks.length > 0 && (
                  <div>
                    <span className="font-medium">Subtasks:</span> {allSubtasks.length}
                  </div>
                )}
              </div>

              {task.status === 'in_progress' && (
                <div className="mb-3">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span>Progress</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <Progress value={progress} className="h-1.5" />
                </div>
              )}

              {task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {task.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {task.tags.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{task.tags.length - 3}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end gap-2 ml-4">
            {task.assignedAgent && (
              <div className="flex items-center gap-2">
                <Avatar className="w-6 h-6">
                  <AvatarFallback className="text-xs bg-blue-100 text-blue-700">
                    AI
                  </AvatarFallback>
                </Avatar>
                <span className="text-xs text-muted-foreground">
                  {task.assignedAgent}
                </span>
              </div>
            )}

            <div className="flex items-center gap-1">
              <Button variant="ghost" size="icon" className="w-6 h-6">
                <ArrowUp className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="icon" className="w-6 h-6">
                <ArrowDown className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="icon" className="w-6 h-6">
                <MoreHorizontal className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-border">
          <div className="flex items-center gap-2">
            {task.dependencies.length > 0 && (
              <Badge variant="outline" className="text-xs">
                {task.dependencies.length} dependencies
              </Badge>
            )}
            {task.status === 'blocked' && (
              <Badge variant="destructive" className="text-xs">
                Blocked
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            {task.status === 'pending' && (
              <Button size="sm" variant="outline" className="text-xs h-7">
                <Play className="w-3 h-3 mr-1" />
                Start
              </Button>
            )}
            {task.status === 'in_progress' && (
              <Button size="sm" variant="outline" className="text-xs h-7">
                <Pause className="w-3 h-3 mr-1" />
                Pause
              </Button>
            )}
            <Button size="sm" variant="ghost" className="text-xs h-7">
              Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function TaskQueue({ tasks }: TaskQueueProps) {
  // Flatten all tasks and subtasks
  const allTasks: (Task & { isSubtask?: boolean; parentId?: string })[] = []

  tasks.forEach(task => {
    allTasks.push(task)
    task.subtasks?.forEach(subtask => {
      allTasks.push({ ...subtask, isSubtask: true, parentId: task.id })
    })
  })

  // Sort by priority and status
  const queuedTasks = allTasks
    .filter(task => task.status !== 'completed')
    .sort((a, b) => {
      const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 }
      const statusOrder = { in_progress: 4, blocked: 3, pending: 2, completed: 1 }

      if (statusOrder[a.status] !== statusOrder[b.status]) {
        return statusOrder[b.status] - statusOrder[a.status]
      }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    })

  const completedTasks = allTasks.filter(task => task.status === 'completed')

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Active Queue */}
      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Active Queue
              </div>
              <Badge variant="secondary">
                {queuedTasks.length} tasks
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-0">
              {queuedTasks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                  <p>All tasks completed!</p>
                </div>
              ) : (
                queuedTasks.map((task, index) => (
                  <QueuedTaskCard
                    key={task.id}
                    task={task}
                    position={index}
                  />
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Queue Stats & Controls */}
      <div className="space-y-6">
        {/* Queue Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Queue Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">In Progress</span>
                <span className="font-semibold">
                  {queuedTasks.filter(t => t.status === 'in_progress').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Pending</span>
                <span className="font-semibold">
                  {queuedTasks.filter(t => t.status === 'pending').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Blocked</span>
                <span className="font-semibold text-red-600">
                  {queuedTasks.filter(t => t.status === 'blocked').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Completed</span>
                <span className="font-semibold text-green-600">
                  {completedTasks.length}
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-border">
              <div className="text-sm text-muted-foreground mb-2">Estimated Time Remaining</div>
              <div className="text-2xl font-bold text-primary">
                {Math.round(queuedTasks.reduce((sum, task) => {
                  const remaining = task.estimatedTime - (task.actualTime || 0)
                  return sum + Math.max(0, remaining)
                }, 0) / 60)}h
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Controls */}
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
              <Bot className="w-5 h-5" />
              AI Queue Manager
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full" variant="outline">
              <Bot className="w-4 h-4 mr-2" />
              Auto-Optimize Queue
            </Button>
            <Button className="w-full" variant="outline">
              <Clock className="w-4 h-4 mr-2" />
              Rebalance Priorities
            </Button>
            <Button className="w-full" variant="outline">
              <Play className="w-4 h-4 mr-2" />
              Start Next Task
            </Button>

            <div className="pt-3 border-t border-border">
              <p className="text-sm text-purple-700 dark:text-purple-300">
                AI suggests processing tasks in parallel to reduce completion time by 35%
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Recently Completed */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Recently Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {completedTasks.slice(-3).map((task) => (
                <div key={task.id} className="flex items-center gap-3 p-2 rounded border">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{task.title}</div>
                    <div className="text-xs text-muted-foreground">
                      Completed {new Date().toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}