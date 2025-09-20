"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Bot,
  Target,
  AlertTriangle,
  Clock,
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

interface TaskMatrixProps {
  tasks: Task[]
}

// Eisenhower Matrix: Urgent vs Important
const getMatrixPosition = (task: Task) => {
  const now = new Date()
  const dueDate = task.dueDate ? new Date(task.dueDate) : null
  const daysUntilDue = dueDate ? Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)) : null

  // Determine urgency based on due date and priority
  const isUrgent = task.priority === 'urgent' ||
                  (dueDate && daysUntilDue !== null && daysUntilDue <= 2) ||
                  task.status === 'blocked'

  // Determine importance based on priority and business impact
  const isImportant = task.priority === 'urgent' ||
                     task.priority === 'high' ||
                     task.tags.includes('business-critical') ||
                     task.tags.includes('client') ||
                     task.subtasks.length > 0

  return {
    urgent: isUrgent,
    important: isImportant
  }
}

function MatrixQuadrant({
  title,
  description,
  tasks,
  color,
  icon: Icon,
  actionText
}: {
  title: string
  description: string
  tasks: Task[]
  color: string
  icon: any
  actionText: string
}) {
  return (
    <Card className={`${color} transition-all hover:shadow-md`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg">
          <div className="flex items-center gap-2">
            <Icon className="w-5 h-5" />
            {title}
          </div>
          <Badge variant="secondary" className="bg-white/80">
            {tasks.length}
          </Badge>
        </CardTitle>
        <p className="text-sm opacity-80">{description}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {tasks.length === 0 ? (
            <div className="text-center py-4 text-white/60">
              No tasks in this quadrant
            </div>
          ) : (
            tasks.map((task) => {
              const allSubtasks = [task, ...(task.subtasks || [])]

              return allSubtasks.map((item, index) => (
                <div
                  key={`${item.id}-${index}`}
                  className={`p-3 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all ${
                    index > 0 ? 'ml-4 border-l-2 border-l-white/40' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-white text-sm truncate">
                        {index > 0 ? '↳ ' : ''}{item.title}
                      </h4>
                      <p className="text-xs text-white/70 mt-1 line-clamp-2">
                        {item.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline" className="text-xs border-white/30 text-white/80">
                          {item.priority}
                        </Badge>
                        {item.aiGenerated && (
                          <Badge variant="outline" className="text-xs border-white/30 text-white/80">
                            <Bot className="w-3 h-3 mr-1" />
                            AI
                          </Badge>
                        )}
                        <span className="text-xs text-white/60">
                          {Math.round(item.estimatedTime / 60)}h
                        </span>
                      </div>
                    </div>
                    {item.assignedAgent && (
                      <div className="text-xs text-white/60 ml-2">
                        {item.assignedAgent}
                      </div>
                    )}
                  </div>
                </div>
              ))
            })
          )}
        </div>

        {tasks.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            className="w-full bg-white/10 border-white/30 text-white hover:bg-white/20"
          >
            {actionText}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

export function TaskMatrix({ tasks }: TaskMatrixProps) {
  // Categorize all tasks (including subtasks) into matrix quadrants
  const allTasks: Task[] = []
  tasks.forEach(task => {
    allTasks.push(task)
    task.subtasks?.forEach(subtask => {
      allTasks.push(subtask)
    })
  })

  const activeTasksOnly = allTasks.filter(task => task.status !== 'completed')

  const quadrants = {
    urgentImportant: activeTasksOnly.filter(task => {
      const pos = getMatrixPosition(task)
      return pos.urgent && pos.important
    }),
    importantNotUrgent: activeTasksOnly.filter(task => {
      const pos = getMatrixPosition(task)
      return !pos.urgent && pos.important
    }),
    urgentNotImportant: activeTasksOnly.filter(task => {
      const pos = getMatrixPosition(task)
      return pos.urgent && !pos.important
    }),
    neitherUrgentNorImportant: activeTasksOnly.filter(task => {
      const pos = getMatrixPosition(task)
      return !pos.urgent && !pos.important
    })
  }

  return (
    <div className="space-y-6">
      {/* Matrix Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MatrixQuadrant
          title="Do First"
          description="Urgent & Important - Crisis mode, handle immediately"
          tasks={quadrants.urgentImportant}
          color="bg-gradient-to-br from-red-500 to-red-600 text-white"
          icon={AlertTriangle}
          actionText="Handle Crisis"
        />

        <MatrixQuadrant
          title="Schedule"
          description="Important but Not Urgent - Plan and focus time"
          tasks={quadrants.importantNotUrgent}
          color="bg-gradient-to-br from-blue-500 to-blue-600 text-white"
          icon={Target}
          actionText="Schedule Focus Time"
        />

        <MatrixQuadrant
          title="Delegate"
          description="Urgent but Not Important - Let AI agents handle"
          tasks={quadrants.urgentNotImportant}
          color="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white"
          icon={Bot}
          actionText="Auto-Delegate"
        />

        <MatrixQuadrant
          title="Eliminate"
          description="Neither Urgent nor Important - Consider removing"
          tasks={quadrants.neitherUrgentNorImportant}
          color="bg-gradient-to-br from-gray-500 to-gray-600 text-white"
          icon={Clock}
          actionText="Review & Remove"
        />
      </div>

      {/* AI Recommendations */}
      <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 border-purple-200 dark:border-purple-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
            <Bot className="w-5 h-5" />
            AI Priority Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="font-semibold text-purple-900 dark:text-purple-100">Immediate Actions</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-2" />
                  <p className="text-sm">
                    <strong>{quadrants.urgentImportant.length} critical tasks</strong> need immediate attention
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2" />
                  <p className="text-sm">
                    <strong>{quadrants.urgentNotImportant.length} tasks</strong> can be auto-delegated to AI agents
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-purple-900 dark:text-purple-100">Strategic Planning</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                  <p className="text-sm">
                    <strong>{quadrants.importantNotUrgent.length} strategic tasks</strong> should be scheduled for focused work
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full mt-2" />
                  <p className="text-sm">
                    <strong>{quadrants.neitherUrgentNorImportant.length} low-priority tasks</strong> could be eliminated
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-4 border-t border-purple-200 dark:border-purple-800">
            <Button className="bg-purple-600 hover:bg-purple-700 text-white">
              <Zap className="w-4 h-4 mr-2" />
              Apply AI Recommendations
            </Button>
            <Button variant="outline" className="border-purple-200 text-purple-700 hover:bg-purple-50">
              <Bot className="w-4 h-4 mr-2" />
              Auto-Delegate Yellow Quadrant
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Matrix Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Priority Matrix Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">How tasks are categorized:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <strong>Urgent:</strong> Due within 2 days, marked urgent, or blocked</li>
                <li>• <strong>Important:</strong> High priority, client-facing, or has subtasks</li>
                <li>• <strong>AI Generated:</strong> Tasks broken down by AI agents</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Recommended actions:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• <strong>Red:</strong> Handle personally and immediately</li>
                <li>• <strong>Blue:</strong> Schedule dedicated time blocks</li>
                <li>• <strong>Yellow:</strong> Perfect for AI agent delegation</li>
                <li>• <strong>Gray:</strong> Question if these tasks are necessary</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}