"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { formatTime } from "@/lib/utils"
import {
  Calendar,
  Clock,
  Users,
  MapPin,
  FileText,
  Bot,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  PlayCircle
} from "lucide-react"

interface Meeting {
  id: string
  title: string
  time: Date
  duration: number
  attendees: string[]
  type: 'internal' | 'client' | 'interview' | 'presentation'
  status: 'upcoming' | 'in_progress' | 'completed' | 'cancelled'
  preparation: {
    status: 'completed' | 'in_progress' | 'pending'
    agenda: boolean
    materials: boolean
    brief: boolean
    aiGenerated: boolean
  }
  location?: string
  description?: string
}

interface MeetingCardProps {
  meeting: Meeting
}

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
  }
}

const getStatusColor = (status: Meeting['status']) => {
  switch (status) {
    case 'upcoming':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    case 'in_progress':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'completed':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
    case 'cancelled':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
  }
}

const getPreparationProgress = (preparation: Meeting['preparation']) => {
  const items = [preparation.agenda, preparation.materials, preparation.brief]
  const completed = items.filter(Boolean).length
  return (completed / items.length) * 100
}

export function MeetingCard({ meeting }: MeetingCardProps) {
  const preparationProgress = getPreparationProgress(meeting.preparation)
  const isUpcoming = meeting.time.getTime() - Date.now() < 60 * 60 * 1000 // Within 1 hour
  const isPast = meeting.time.getTime() < Date.now()

  return (
    <Card className={`transition-all hover:shadow-md ${
      isUpcoming && !isPast ? 'border-orange-200 bg-orange-50/30 dark:border-orange-800 dark:bg-orange-950/10' : ''
    }`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={getTypeColor(meeting.type)}>
                {meeting.type}
              </Badge>
              <Badge variant="outline" className={getStatusColor(meeting.status)}>
                {meeting.status}
              </Badge>
              {meeting.preparation.aiGenerated && (
                <Badge variant="outline" className="bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                  <Bot className="w-3 h-3 mr-1" />
                  AI
                </Badge>
              )}
            </div>
            <h3 className="font-semibold text-lg leading-tight">
              {meeting.title}
            </h3>
            {meeting.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {meeting.description}
              </p>
            )}
          </div>
          {isUpcoming && !isPast && (
            <div className="flex items-center gap-1 text-orange-600 dark:text-orange-400">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Soon</span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Meeting Details */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span>{formatTime(meeting.time)}</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span>{meeting.duration} minutes</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Users className="w-4 h-4" />
            <span>{meeting.attendees.length} attendees</span>
          </div>
          {meeting.location && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="w-4 h-4" />
              <span className="truncate">{meeting.location}</span>
            </div>
          )}
        </div>

        {/* Attendees */}
        <div>
          <p className="text-sm font-medium mb-2">Attendees</p>
          <div className="flex items-center gap-2">
            <div className="flex -space-x-2">
              {meeting.attendees.slice(0, 3).map((attendee, index) => (
                <Avatar key={index} className="w-8 h-8 border-2 border-background">
                  <AvatarFallback className="text-xs">
                    {attendee.split(' ').map(n => n[0]).join('').substring(0, 2)}
                  </AvatarFallback>
                </Avatar>
              ))}
              {meeting.attendees.length > 3 && (
                <div className="w-8 h-8 bg-muted rounded-full border-2 border-background flex items-center justify-center">
                  <span className="text-xs text-muted-foreground">
                    +{meeting.attendees.length - 3}
                  </span>
                </div>
              )}
            </div>
            <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
              {meeting.attendees.slice(0, 2).map((attendee, index) => (
                <span key={index} className="truncate">
                  {attendee}{index < Math.min(meeting.attendees.length, 2) - 1 ? ',' : ''}
                </span>
              ))}
              {meeting.attendees.length > 2 && (
                <span>+{meeting.attendees.length - 2} more</span>
              )}
            </div>
          </div>
        </div>

        {/* Preparation Status */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">Preparation Status</p>
            <div className="flex items-center gap-2">
              {meeting.preparation.status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : meeting.preparation.status === 'in_progress' ? (
                <PlayCircle className="w-4 h-4 text-yellow-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm capitalize">
                {meeting.preparation.status.replace('_', ' ')}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span>Progress</span>
              <span>{Math.round(preparationProgress)}% complete</span>
            </div>
            <Progress value={preparationProgress} className="h-2" />
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                meeting.preparation.agenda ? 'bg-green-500' : 'bg-gray-300'
              }`} />
              <span>Agenda</span>
            </div>
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                meeting.preparation.materials ? 'bg-green-500' : 'bg-gray-300'
              }`} />
              <span>Materials</span>
            </div>
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                meeting.preparation.brief ? 'bg-green-500' : 'bg-gray-300'
              }`} />
              <span>Brief</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2 border-t border-border">
          <Button variant="outline" size="sm" className="flex-1">
            <FileText className="w-4 h-4 mr-2" />
            View Details
          </Button>
          {meeting.status === 'upcoming' && (
            <Button size="sm" className="flex-1">
              {meeting.preparation.status === 'completed' ? 'Join Meeting' : 'Prepare'}
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}