"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { formatTime } from "@/lib/utils"
import {
  Calendar,
  Clock,
  Users,
  FileText,
  ChevronRight,
  Bot,
  AlertCircle
} from "lucide-react"

interface Meeting {
  id: string
  title: string
  time: Date
  duration: number
  attendees: string[]
  type: 'internal' | 'client' | 'interview' | 'presentation'
  preparation: {
    status: 'completed' | 'in_progress' | 'pending'
    agenda: boolean
    materials: boolean
    brief: boolean
  }
  aiGenerated?: {
    agenda?: boolean
    brief?: boolean
    materials?: boolean
  }
}

const mockMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Client Strategy Review - TechCorp',
    time: new Date(Date.now() + 30 * 60 * 1000), // 30 minutes from now
    duration: 60,
    attendees: ['John Smith', 'Sarah Wilson', 'Mike Johnson'],
    type: 'client',
    preparation: {
      status: 'completed',
      agenda: true,
      materials: true,
      brief: true
    },
    aiGenerated: {
      agenda: true,
      brief: true,
      materials: true
    }
  },
  {
    id: '2',
    title: 'Team Standup - Engineering',
    time: new Date(Date.now() + 2 * 60 * 60 * 1000), // 2 hours from now
    duration: 30,
    attendees: ['Dev Team'],
    type: 'internal',
    preparation: {
      status: 'in_progress',
      agenda: true,
      materials: false,
      brief: true
    },
    aiGenerated: {
      agenda: true,
      brief: true
    }
  },
  {
    id: '3',
    title: 'Product Demo - Stakeholders',
    time: new Date(Date.now() + 4 * 60 * 60 * 1000), // 4 hours from now
    duration: 45,
    attendees: ['CEO', 'CTO', 'Product Team', 'Sales Team'],
    type: 'presentation',
    preparation: {
      status: 'pending',
      agenda: false,
      materials: false,
      brief: false
    }
  },
  {
    id: '4',
    title: 'Candidate Interview - Senior Developer',
    time: new Date(Date.now() + 6 * 60 * 60 * 1000), // 6 hours from now
    duration: 60,
    attendees: ['HR', 'Engineering Lead'],
    type: 'interview',
    preparation: {
      status: 'completed',
      agenda: true,
      materials: true,
      brief: true
    },
    aiGenerated: {
      agenda: true,
      brief: true
    }
  }
]

const getTypeColor = (type: Meeting['type']) => {
  switch (type) {
    case 'client':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    case 'internal':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'interview':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100'
    case 'presentation':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
  }
}

const getPreparationStatus = (status: Meeting['preparation']['status']) => {
  switch (status) {
    case 'completed':
      return {
        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
        text: 'Ready'
      }
    case 'in_progress':
      return {
        color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
        text: 'Preparing'
      }
    case 'pending':
      return {
        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
        text: 'Needs Prep'
      }
  }
}

export function ScheduleOverview() {
  const upcomingMeetings = mockMeetings.slice(0, 3)
  const needsPreparation = mockMeetings.filter(m => m.preparation.status !== 'completed').length

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Today's Schedule
          </div>
          {needsPreparation > 0 && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {needsPreparation} need prep
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {upcomingMeetings.map((meeting) => {
            const prepStatus = getPreparationStatus(meeting.preparation.status)
            const isUpcoming = meeting.time.getTime() - Date.now() < 60 * 60 * 1000 // Within 1 hour

            return (
              <div
                key={meeting.id}
                className={`p-4 rounded-lg border transition-all hover:shadow-sm ${
                  isUpcoming ? 'border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950/20' : 'border-border'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-medium text-sm mb-1">{meeting.title}</h4>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className={getTypeColor(meeting.type)}>
                        {meeting.type}
                      </Badge>
                      <Badge variant="outline" className={prepStatus.color}>
                        {prepStatus.text}
                      </Badge>
                    </div>
                  </div>
                  {isUpcoming && (
                    <div className="flex items-center gap-1 text-orange-600 dark:text-orange-400">
                      <Clock className="w-3 h-3" />
                      <span className="text-xs">Soon</span>
                    </div>
                  )}
                </div>

                <div className="space-y-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(meeting.time)} ({meeting.duration}min)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-3 h-3" />
                    <span>{meeting.attendees.length} attendees</span>
                  </div>

                  {/* AI Preparation Status */}
                  {meeting.aiGenerated && (
                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border">
                      <Bot className="w-3 h-3 text-blue-500" />
                      <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                        {meeting.aiGenerated.agenda && (
                          <span className="text-xs">Agenda</span>
                        )}
                        {meeting.aiGenerated.brief && (
                          <span className="text-xs">Brief</span>
                        )}
                        {meeting.aiGenerated.materials && (
                          <span className="text-xs">Materials</span>
                        )}
                        <span className="text-xs">AI-prepared</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Quick Actions */}
        <div className="pt-2 border-t border-border space-y-2">
          <Button variant="outline" size="sm" className="w-full justify-between">
            View Full Calendar
            <ChevronRight className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4" />
              AI Schedule Optimization
            </div>
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        {/* Daily Summary */}
        <div className="pt-2 border-t border-border">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-primary">{mockMeetings.length}</div>
              <div className="text-xs text-muted-foreground">Total Meetings</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-blue-600">
                {mockMeetings.reduce((sum, m) => sum + m.duration, 0)}m
              </div>
              <div className="text-xs text-muted-foreground">Total Time</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}