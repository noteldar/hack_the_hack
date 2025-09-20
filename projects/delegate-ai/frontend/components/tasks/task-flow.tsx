"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  CheckCircle,
  Clock,
  Play,
  AlertTriangle,
  Bot,
  ArrowDown,
  ChevronRight,
  Zap
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

interface TaskFlowProps {
  tasks: Task[]
}

const getStatusIcon = (status: Task['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />
    case 'in_progress':
      return <Play className="w-5 h-5 text-blue-500" />
    case 'blocked':
      return <AlertTriangle className="w-5 h-5 text-red-500" />
    case 'pending':
      return <Clock className="w-5 h-5 text-gray-500" />
  }
}

const getPriorityColor = (priority: Task['priority']) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
    case 'high':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
  }
}

const getProgressPercentage = (task: Task) => {
  if (task.status === 'completed') return 100
  if (task.status === 'pending') return 0
  if (task.actualTime && task.estimatedTime) {
    return Math.min((task.actualTime / task.estimatedTime) * 100, 100)
  }
  return 25 // Default for in-progress without time data
}

function TaskCard({ task, level = 0 }: { task: Task; level?: number }) {
  const progress = getProgressPercentage(task)
  const hasSubtasks = task.subtasks && task.subtasks.length > 0

  return (
    <div className={`ml-${level * 6}`}>
      <Card className={`mb-4 transition-all hover:shadow-md ${
        task.status === 'in_progress' ? 'border-blue-200 bg-blue-50/30 dark:border-blue-800 dark:bg-blue-950/10' : ''
      }`}>
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-3 flex-1">
              <div className="mt-1">
                {getStatusIcon(task.status)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-semibold text-lg truncate">
                    {task.title}
                  </h4>
                  <Badge variant="outline" className={getPriorityColor(task.priority)}>
                    {task.priority}
                  </Badge>
                  {task.aiGenerated && (
                    <Badge variant="outline" className="bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                      <Bot className="w-3 h-3 mr-1" />
                      AI
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                  {task.description}
                </p>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Est: {Math.round(task.estimatedTime / 60)}h</span>
                  {task.actualTime && (
                    <span>Actual: {Math.round(task.actualTime / 60)}h</span>
                  )}
                  {task.dueDate && (
                    <span>Due: {task.dueDate.toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            </div>

            {task.assignedAgent && (
              <div className="flex items-center gap-2 ml-4">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="text-xs bg-blue-100 text-blue-700">
                    AI
                  </AvatarFallback>
                </Avatar>
                <div className="text-right">
                  <div className="text-xs font-medium">{task.assignedAgent}</div>
                  <div className="text-xs text-muted-foreground">Assigned</div>
                </div>
              </div>
            )}
          </div>

          {/* Progress */}
          {task.status === 'in_progress' && (
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="font-medium">Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}

          {/* Tags */}
          {task.tags.length > 0 && (
            <div className="flex items-center gap-2 mb-4">
              {task.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <div className="flex items-center gap-2">
              {hasSubtasks && (
                <Badge variant="outline" className="text-xs">
                  {task.subtasks.length} subtasks
                </Badge>
              )}
              {task.dependencies.length > 0 && (
                <Badge variant="outline" className="text-xs">
                  {task.dependencies.length} dependencies
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              {task.status === 'pending' && (
                <Button size="sm" variant="outline">
                  <Play className="w-4 h-4 mr-2" />
                  Start
                </Button>
              )}
              {task.status === 'in_progress' && (
                <Button size="sm" variant="outline">
                  <Zap className="w-4 h-4 mr-2" />
                  Accelerate
                </Button>
              )}
              <Button size="sm" variant="ghost">
                Details
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Subtasks */}
      {hasSubtasks && (
        <div className="ml-8 relative">
          {/* Connection line */}
          <div className="absolute left-[-16px] top-0 bottom-0 w-0.5 bg-border" />

          {task.subtasks.map((subtask, index) => (
            <div key={subtask.id} className="relative">
              {/* Horizontal connection */}
              <div className="absolute left-[-16px] top-6 w-4 h-0.5 bg-border" />

              {/* Subtask card */}
              <div className="mb-4">
                <Card className="bg-muted/30 border-dashed">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(subtask.status)}
                        <div className="flex-1">
                          <h5 className="font-medium text-sm">{subtask.title}</h5>
                          <p className="text-xs text-muted-foreground mt-1">
                            {subtask.description}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className={getPriorityColor(subtask.priority)}>
                              {subtask.priority}
                            </Badge>
                            {subtask.aiGenerated && (
                              <Badge variant="outline" className="bg-purple-50 text-purple-700 text-xs">
                                <Bot className="w-3 h-3 mr-1" />
                                AI
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      {subtask.assignedAgent && (
                        <div className="text-xs text-muted-foreground ml-4">
                          {subtask.assignedAgent}
                        </div>
                      )}
                    </div>

                    {subtask.status === 'in_progress' && (
                      <div className="mt-3">
                        <Progress value={getProgressPercentage(subtask)} className="h-1" />
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Arrow to next subtask */}
              {index < task.subtasks.length - 1 && (
                <div className="flex justify-center mb-2">
                  <ArrowDown className="w-4 h-4 text-muted-foreground" />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function TaskFlow({ tasks }: TaskFlowProps) {
  // Sort tasks by priority and status
  const sortedTasks = [...tasks].sort((a, b) => {
    const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 }
    const statusOrder = { in_progress: 4, pending: 3, blocked: 2, completed: 1 }

    if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    }
    return statusOrder[b.status] - statusOrder[a.status]
  })

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Autonomous Task Execution Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sortedTasks.map((task, index) => (
              <div key={task.id}>
                <TaskCard task={task} />
                {index < sortedTasks.length - 1 && (
                  <div className="flex justify-center mb-4">
                    <ArrowDown className="w-5 h-5 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI Insights */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
            <Bot className="w-5 h-5" />
            AI Orchestration Insights
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Parallel processing</strong> enabled for subtasks 1b and 1c after 1a completion
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Resource optimization</strong> suggests combining similar tasks to reduce context switching
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Dependency analysis</strong> shows critical path can be reduced by 2 hours with agent coordination
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}