"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { formatTime, getTimeAgo } from "@/lib/utils"
import {
  Mail,
  Send,
  Bot,
  Reply,
  Forward,
  Archive,
  Star,
  Clock,
  CheckCircle,
  AlertCircle
} from "lucide-react"

interface TimelineEvent {
  id: string
  type: 'email_received' | 'email_sent' | 'ai_response_generated' | 'email_starred' | 'email_archived' | 'meeting_scheduled'
  timestamp: Date
  title: string
  description: string
  participants: string[]
  metadata?: {
    emailSubject?: string
    aiConfidence?: number
    responseTime?: number
    category?: string
  }
}

const mockTimelineEvents: TimelineEvent[] = [
  {
    id: '1',
    type: 'ai_response_generated',
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    title: 'AI Response Generated',
    description: 'Draft response created for client inquiry about Q4 budget',
    participants: ['AI Assistant', 'John Smith (TechCorp)'],
    metadata: {
      emailSubject: 'Q4 Budget Review Meeting',
      aiConfidence: 92,
      responseTime: 45
    }
  },
  {
    id: '2',
    type: 'email_received',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    title: 'Email Received',
    description: 'High priority email from existing client',
    participants: ['John Smith (TechCorp)'],
    metadata: {
      emailSubject: 'Q4 Budget Review Meeting',
      category: 'client'
    }
  },
  {
    id: '3',
    type: 'email_sent',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    title: 'Email Sent',
    description: 'Response sent to partnership inquiry',
    participants: ['Lisa Chen (Startup.io)'],
    metadata: {
      emailSubject: 'Partnership Opportunity',
      responseTime: 25
    }
  },
  {
    id: '4',
    type: 'meeting_scheduled',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    title: 'Meeting Scheduled',
    description: 'Follow-up meeting automatically scheduled via AI',
    participants: ['Sarah Wilson', 'Product Team'],
    metadata: {
      emailSubject: 'Project Alpha Status Update'
    }
  },
  {
    id: '5',
    type: 'email_archived',
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    title: 'Email Archived',
    description: 'Marketing newsletter automatically archived',
    participants: ['Marketing Team'],
    metadata: {
      emailSubject: 'Weekly Newsletter - Industry Updates',
      category: 'marketing'
    }
  },
  {
    id: '6',
    type: 'ai_response_generated',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    title: 'AI Response Generated',
    description: 'Professional response drafted for vendor inquiry',
    participants: ['AI Assistant', 'Mike Johnson (Vendor)'],
    metadata: {
      emailSubject: 'Invoice #12345 - Payment Terms',
      aiConfidence: 65,
      responseTime: 12
    }
  },
  {
    id: '7',
    type: 'email_starred',
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
    title: 'Email Starred',
    description: 'Important client communication marked for follow-up',
    participants: ['John Smith (TechCorp)'],
    metadata: {
      emailSubject: 'Contract Renewal Discussion',
      category: 'client'
    }
  },
  {
    id: '8',
    type: 'email_received',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    title: 'Email Received',
    description: 'New partnership opportunity from startup',
    participants: ['Lisa Chen (Startup.io)'],
    metadata: {
      emailSubject: 'Partnership Opportunity',
      category: 'client'
    }
  }
]

const getEventIcon = (type: TimelineEvent['type']) => {
  switch (type) {
    case 'email_received':
      return <Mail className="w-4 h-4 text-blue-500" />
    case 'email_sent':
      return <Send className="w-4 h-4 text-green-500" />
    case 'ai_response_generated':
      return <Bot className="w-4 h-4 text-purple-500" />
    case 'email_starred':
      return <Star className="w-4 h-4 text-yellow-500" />
    case 'email_archived':
      return <Archive className="w-4 h-4 text-gray-500" />
    case 'meeting_scheduled':
      return <CheckCircle className="w-4 h-4 text-green-600" />
    default:
      return <Clock className="w-4 h-4 text-gray-500" />
  }
}

const getEventColor = (type: TimelineEvent['type']) => {
  switch (type) {
    case 'email_received':
      return 'border-blue-200 bg-blue-50 dark:bg-blue-950/20'
    case 'email_sent':
      return 'border-green-200 bg-green-50 dark:bg-green-950/20'
    case 'ai_response_generated':
      return 'border-purple-200 bg-purple-50 dark:bg-purple-950/20'
    case 'email_starred':
      return 'border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20'
    case 'email_archived':
      return 'border-gray-200 bg-gray-50 dark:bg-gray-950/20'
    case 'meeting_scheduled':
      return 'border-green-200 bg-green-50 dark:bg-green-950/20'
    default:
      return 'border-gray-200 bg-gray-50 dark:bg-gray-950/20'
  }
}

function TimelineEventCard({ event, isLast }: { event: TimelineEvent; isLast: boolean }) {
  return (
    <div className="relative">
      {/* Timeline line */}
      {!isLast && (
        <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-border" />
      )}

      <div className="flex gap-4">
        {/* Event icon */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-full bg-background border-2 border-border flex items-center justify-center">
            {getEventIcon(event.type)}
          </div>
        </div>

        {/* Event content */}
        <div className="flex-1 pb-8">
          <Card className={`transition-all hover:shadow-sm ${getEventColor(event.type)}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-medium text-sm">{event.title}</h4>
                  <p className="text-xs text-muted-foreground">
                    {formatTime(event.timestamp)} • {getTimeAgo(event.timestamp)}
                  </p>
                </div>
                {event.metadata?.aiConfidence && (
                  <Badge variant="outline" className="bg-white/80">
                    {event.metadata.aiConfidence}% AI
                  </Badge>
                )}
              </div>

              <p className="text-sm text-muted-foreground mb-3">
                {event.description}
              </p>

              {/* Metadata */}
              {event.metadata && (
                <div className="space-y-2 mb-3">
                  {event.metadata.emailSubject && (
                    <div className="text-xs">
                      <span className="font-medium">Subject:</span>{' '}
                      <span className="text-muted-foreground">{event.metadata.emailSubject}</span>
                    </div>
                  )}
                  {event.metadata.responseTime && (
                    <div className="text-xs">
                      <span className="font-medium">Response time:</span>{' '}
                      <span className="text-green-600">{event.metadata.responseTime}s</span>
                    </div>
                  )}
                  {event.metadata.category && (
                    <Badge variant="outline" className="text-xs">
                      {event.metadata.category}
                    </Badge>
                  )}
                </div>
              )}

              {/* Participants */}
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {event.participants.slice(0, 3).map((participant, index) => (
                    <Avatar key={index} className="w-6 h-6 border border-background">
                      <AvatarFallback className="text-xs">
                        {participant.includes('AI') ? (
                          <Bot className="w-3 h-3" />
                        ) : (
                          participant.split(' ').map(n => n[0]).join('').substring(0, 2)
                        )}
                      </AvatarFallback>
                    </Avatar>
                  ))}
                  {event.participants.length > 3 && (
                    <div className="w-6 h-6 bg-muted rounded-full border border-background flex items-center justify-center">
                      <span className="text-xs text-muted-foreground">
                        +{event.participants.length - 3}
                      </span>
                    </div>
                  )}
                </div>
                <div className="text-xs text-muted-foreground">
                  {event.participants.slice(0, 2).join(', ')}
                  {event.participants.length > 2 && ` +${event.participants.length - 2} more`}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export function CommunicationTimeline() {
  const todayEvents = mockTimelineEvents.filter(event => {
    const today = new Date()
    const eventDate = new Date(event.timestamp)
    return eventDate.toDateString() === today.toDateString()
  })

  const aiEvents = mockTimelineEvents.filter(event => event.type === 'ai_response_generated')
  const avgResponseTime = aiEvents.length > 0
    ? Math.round(aiEvents.reduce((sum, event) => sum + (event.metadata?.responseTime || 0), 0) / aiEvents.length)
    : 0

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Timeline */}
      <div className="lg:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Communication Timeline
              <Badge variant="secondary">Today</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {todayEvents.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>No communication activity today</p>
              </div>
            ) : (
              <div className="space-y-0">
                {todayEvents.map((event, index) => (
                  <TimelineEventCard
                    key={event.id}
                    event={event}
                    isLast={index === todayEvents.length - 1}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sidebar Stats */}
      <div className="space-y-4">
        {/* Today's Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Today's Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-blue-500" />
                <span className="text-sm">Received</span>
              </div>
              <Badge variant="outline">
                {todayEvents.filter(e => e.type === 'email_received').length}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-green-500" />
                <span className="text-sm">Sent</span>
              </div>
              <Badge variant="outline">
                {todayEvents.filter(e => e.type === 'email_sent').length}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-purple-500" />
                <span className="text-sm">AI Drafted</span>
              </div>
              <Badge variant="outline">
                {todayEvents.filter(e => e.type === 'ai_response_generated').length}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm">Avg AI Response Time</span>
                <span className="text-sm font-medium">{avgResponseTime}s</span>
              </div>
              <div className="text-xs text-green-600">15% faster than yesterday</div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm">AI Accuracy</span>
                <span className="text-sm font-medium">
                  {aiEvents.length > 0
                    ? Math.round(aiEvents.reduce((sum, e) => sum + (e.metadata?.aiConfidence || 0), 0) / aiEvents.length)
                    : 0}%
                </span>
              </div>
              <div className="text-xs text-green-600">+3% from last week</div>
            </div>
          </CardContent>
        </Card>

        {/* Filter Options */}
        <Card>
          <CardHeader>
            <CardTitle>Filter Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">All Events</span>
              <Badge variant="secondary">{mockTimelineEvents.length}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">AI Actions</span>
              <Badge variant="outline">{aiEvents.length}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Client Emails</span>
              <Badge variant="outline">
                {mockTimelineEvents.filter(e => e.metadata?.category === 'client').length}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Internal</span>
              <Badge variant="outline">
                {mockTimelineEvents.filter(e => e.metadata?.category === 'internal').length}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}