"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { formatTime } from "@/lib/utils"
import { Bot, CheckCircle, Clock, Mail, Calendar, Users } from "lucide-react"

interface ActivityItem {
  id: string
  type: 'task_completed' | 'meeting_scheduled' | 'email_sent' | 'task_created' | 'collaboration'
  title: string
  description: string
  timestamp: Date
  agent: string
  priority?: 'low' | 'medium' | 'high'
}

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'task_completed',
    title: 'Email Draft Completed',
    description: 'Drafted response to client inquiry about Q4 projections',
    timestamp: new Date(Date.now() - 2 * 60 * 1000), // 2 minutes ago
    agent: 'Communication Agent',
    priority: 'high'
  },
  {
    id: '2',
    type: 'meeting_scheduled',
    title: 'Meeting Scheduled',
    description: 'Team sync for project Alpha - agenda prepared and sent',
    timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
    agent: 'Calendar Agent',
    priority: 'medium'
  },
  {
    id: '3',
    type: 'task_created',
    title: 'Task Breakdown',
    description: 'Analyzed "Launch campaign" and created 12 subtasks',
    timestamp: new Date(Date.now() - 8 * 60 * 1000), // 8 minutes ago
    agent: 'Task Agent',
    priority: 'medium'
  },
  {
    id: '4',
    type: 'collaboration',
    title: 'Cross-Agent Coordination',
    description: 'Coordinated with Calendar Agent to reschedule conflicting meetings',
    timestamp: new Date(Date.now() - 12 * 60 * 1000), // 12 minutes ago
    agent: 'Orchestrator',
    priority: 'low'
  },
  {
    id: '5',
    type: 'email_sent',
    title: 'Auto-Response Sent',
    description: 'Replied to 3 routine inquiries with personalized responses',
    timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
    agent: 'Communication Agent',
    priority: 'low'
  }
]

const getActivityIcon = (type: ActivityItem['type']) => {
  switch (type) {
    case 'task_completed':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'meeting_scheduled':
      return <Calendar className="w-4 h-4 text-blue-500" />
    case 'email_sent':
      return <Mail className="w-4 h-4 text-purple-500" />
    case 'task_created':
      return <Clock className="w-4 h-4 text-orange-500" />
    case 'collaboration':
      return <Users className="w-4 h-4 text-pink-500" />
    default:
      return <Bot className="w-4 h-4 text-gray-500" />
  }
}

const getPriorityColor = (priority: ActivityItem['priority']) => {
  switch (priority) {
    case 'high':
      return 'border-l-red-500 bg-red-50 dark:bg-red-950/20'
    case 'medium':
      return 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950/20'
    case 'low':
      return 'border-l-green-500 bg-green-50 dark:bg-green-950/20'
    default:
      return 'border-l-gray-500 bg-gray-50 dark:bg-gray-950/20'
  }
}

export function ActivityFeed() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="w-5 h-5" />
          AI Agent Activity
          <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {mockActivities.map((activity) => (
            <div
              key={activity.id}
              className={`p-3 rounded-lg border-l-4 ${getPriorityColor(activity.priority)} transition-all hover:shadow-sm`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className="mt-1">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm truncate">
                        {activity.title}
                      </h4>
                      {activity.priority && (
                        <Badge
                          variant="outline"
                          className={`text-xs ${
                            activity.priority === 'high'
                              ? 'border-red-200 text-red-700 dark:border-red-800 dark:text-red-300'
                              : activity.priority === 'medium'
                              ? 'border-yellow-200 text-yellow-700 dark:border-yellow-800 dark:text-yellow-300'
                              : 'border-green-200 text-green-700 dark:border-green-800 dark:text-green-300'
                          }`}
                        >
                          {activity.priority}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                      {activity.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Avatar className="w-5 h-5">
                          <AvatarFallback className="text-xs bg-primary/10 text-primary">
                            AI
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-muted-foreground">
                          {activity.agent}
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {formatTime(activity.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t border-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {mockActivities.length} activities in the last hour
            </span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-600 dark:text-green-400">
                Active
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}