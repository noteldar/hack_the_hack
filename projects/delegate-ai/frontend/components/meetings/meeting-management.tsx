"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MeetingCard } from "./meeting-card"
import { MeetingCalendar } from "./meeting-calendar"
import { formatDate } from "@/lib/utils"
import {
  Calendar,
  Plus,
  Search,
  Filter,
  Bot,
  Clock,
  Users,
  TrendingUp
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

const mockMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Client Strategy Review - TechCorp',
    time: new Date(Date.now() + 30 * 60 * 1000),
    duration: 60,
    attendees: ['John Smith', 'Sarah Wilson', 'Mike Johnson'],
    type: 'client',
    status: 'upcoming',
    location: 'Conference Room A',
    description: 'Quarterly review of TechCorp account strategy and next steps',
    preparation: {
      status: 'completed',
      agenda: true,
      materials: true,
      brief: true,
      aiGenerated: true
    }
  },
  {
    id: '2',
    title: 'Team Standup - Engineering',
    time: new Date(Date.now() + 2 * 60 * 60 * 1000),
    duration: 30,
    attendees: ['Dev Team (8)'],
    type: 'internal',
    status: 'upcoming',
    location: 'Zoom',
    preparation: {
      status: 'in_progress',
      agenda: true,
      materials: false,
      brief: true,
      aiGenerated: true
    }
  },
  {
    id: '3',
    title: 'Product Demo - Stakeholders',
    time: new Date(Date.now() + 4 * 60 * 60 * 1000),
    duration: 45,
    attendees: ['CEO', 'CTO', 'Product Team', 'Sales Team'],
    type: 'presentation',
    status: 'upcoming',
    location: 'Main Auditorium',
    description: 'Demo of new product features for Q4 release',
    preparation: {
      status: 'pending',
      agenda: false,
      materials: false,
      brief: false,
      aiGenerated: false
    }
  },
  {
    id: '4',
    title: 'Candidate Interview - Senior Developer',
    time: new Date(Date.now() + 6 * 60 * 60 * 1000),
    duration: 60,
    attendees: ['HR Manager', 'Engineering Lead', 'Team Lead'],
    type: 'interview',
    status: 'upcoming',
    location: 'Conference Room B',
    preparation: {
      status: 'completed',
      agenda: true,
      materials: true,
      brief: true,
      aiGenerated: true
    }
  },
  {
    id: '5',
    title: 'Weekly All-Hands',
    time: new Date(Date.now() - 2 * 60 * 60 * 1000),
    duration: 60,
    attendees: ['All Company (45)'],
    type: 'internal',
    status: 'completed',
    location: 'Main Auditorium',
    preparation: {
      status: 'completed',
      agenda: true,
      materials: true,
      brief: true,
      aiGenerated: true
    }
  }
]

export function MeetingManagement() {
  const upcomingMeetings = mockMeetings.filter(m => m.status === 'upcoming')
  const todaysMeetings = upcomingMeetings.filter(m => {
    const today = new Date()
    const meetingDate = new Date(m.time)
    return meetingDate.toDateString() === today.toDateString()
  })

  const preparationStats = {
    ready: upcomingMeetings.filter(m => m.preparation.status === 'completed').length,
    preparing: upcomingMeetings.filter(m => m.preparation.status === 'in_progress').length,
    needsPrep: upcomingMeetings.filter(m => m.preparation.status === 'pending').length
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meeting Management</h1>
          <p className="text-muted-foreground mt-1">
            AI-powered meeting preparation and management
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Schedule Meeting
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Today's Meetings</p>
                <p className="text-2xl font-bold">{todaysMeetings.length}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ready</p>
                <p className="text-2xl font-bold text-green-600">{preparationStats.ready}</p>
              </div>
              <Bot className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Preparing</p>
                <p className="text-2xl font-bold text-yellow-600">{preparationStats.preparing}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Need Prep</p>
                <p className="text-2xl font-bold text-red-600">{preparationStats.needsPrep}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Preparation Banner */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">
                  AI Meeting Assistant
                </h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Automatically generating agendas, briefs, and materials for upcoming meetings
                </p>
              </div>
            </div>
            <Button variant="secondary" className="bg-white/50 hover:bg-white/70">
              Configure AI
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="list" className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="list">Meeting List</TabsTrigger>
            <TabsTrigger value="calendar">Calendar View</TabsTrigger>
          </TabsList>

          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                type="text"
                placeholder="Search meetings..."
                className="pl-10 w-64"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
          </div>
        </div>

        <TabsContent value="list" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {mockMeetings.map((meeting) => (
              <MeetingCard key={meeting.id} meeting={meeting} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="calendar">
          <MeetingCalendar meetings={mockMeetings} />
        </TabsContent>
      </Tabs>
    </div>
  )
}