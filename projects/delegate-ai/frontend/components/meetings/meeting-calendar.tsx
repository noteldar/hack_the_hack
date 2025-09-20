"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatTime } from "@/lib/utils"
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Bot
} from "lucide-react"
import { useState } from "react"

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

interface MeetingCalendarProps {
  meetings: Meeting[]
}

const getTypeColor = (type: Meeting['type']) => {
  switch (type) {
    case 'client':
      return 'bg-blue-500'
    case 'internal':
      return 'bg-green-500'
    case 'interview':
      return 'bg-purple-500'
    case 'presentation':
      return 'bg-orange-500'
  }
}

export function MeetingCalendar({ meetings }: MeetingCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date())

  // Get current week
  const startOfWeek = new Date(currentDate)
  const dayOfWeek = currentDate.getDay()
  const diff = currentDate.getDate() - dayOfWeek
  startOfWeek.setDate(diff)

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + i)
    return date
  })

  const hours = Array.from({ length: 12 }, (_, i) => i + 8) // 8 AM to 7 PM

  const getMeetingsForDate = (date: Date) => {
    return meetings.filter(meeting => {
      const meetingDate = new Date(meeting.time)
      return meetingDate.toDateString() === date.toDateString()
    })
  }

  const getMeetingPosition = (time: Date) => {
    const hour = time.getHours()
    const minutes = time.getMinutes()
    const position = ((hour - 8) * 60 + minutes) / 60 // Convert to hours from 8 AM
    return Math.max(0, position * 60) // Convert to pixels (60px per hour)
  }

  const getMeetingHeight = (duration: number) => {
    return (duration / 60) * 60 // 60px per hour
  }

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    newDate.setDate(currentDate.getDate() + (direction === 'next' ? 7 : -7))
    setCurrentDate(newDate)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Calendar View
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => navigateWeek('prev')}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="font-medium">
                {startOfWeek.toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric'
                })} - {weekDays[6].toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </span>
              <Button variant="outline" size="sm" onClick={() => navigateWeek('next')}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
              Today
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-8 gap-0 border border-border rounded-lg overflow-hidden">
          {/* Time column header */}
          <div className="bg-muted p-2 border-r border-border">
            <div className="text-sm font-medium">Time</div>
          </div>

          {/* Day headers */}
          {weekDays.map((date, index) => {
            const isToday = date.toDateString() === new Date().toDateString()
            return (
              <div
                key={index}
                className={`p-2 border-r border-border bg-muted ${
                  isToday ? 'bg-blue-50 dark:bg-blue-950/20' : ''
                }`}
              >
                <div className="text-center">
                  <div className="text-xs text-muted-foreground">
                    {date.toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                  <div className={`text-sm font-medium ${
                    isToday ? 'text-blue-600 dark:text-blue-400' : ''
                  }`}>
                    {date.getDate()}
                  </div>
                </div>
              </div>
            )
          })}

          {/* Time slots and meetings */}
          {hours.map((hour) => (
            <>
              {/* Time label */}
              <div key={`time-${hour}`} className="p-2 border-r border-border border-t border-border bg-muted/30">
                <div className="text-xs text-muted-foreground">
                  {hour}:00
                </div>
              </div>

              {/* Day columns */}
              {weekDays.map((date, dayIndex) => {
                const dayMeetings = getMeetingsForDate(date)
                const hourMeetings = dayMeetings.filter(meeting =>
                  new Date(meeting.time).getHours() === hour
                )

                return (
                  <div
                    key={`${dayIndex}-${hour}`}
                    className="relative border-r border-border border-t border-border p-1 h-16 bg-background hover:bg-muted/30 transition-colors"
                  >
                    {hourMeetings.map((meeting) => (
                      <div
                        key={meeting.id}
                        className={`absolute left-1 right-1 rounded p-1 text-xs text-white overflow-hidden ${getTypeColor(meeting.type)}`}
                        style={{
                          top: `${(new Date(meeting.time).getMinutes() / 60) * 100}%`,
                          height: `${Math.min((meeting.duration / 60) * 100, 100)}%`,
                          minHeight: '20px'
                        }}
                      >
                        <div className="flex items-center gap-1">
                          <span className="truncate font-medium">
                            {meeting.title}
                          </span>
                          {meeting.preparation.aiGenerated && (
                            <Bot className="w-3 h-3 shrink-0" />
                          )}
                        </div>
                        <div className="text-xs opacity-90">
                          {formatTime(meeting.time)}
                        </div>
                      </div>
                    ))}
                  </div>
                )
              })}
            </>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-6 mt-4 p-4 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded" />
            <span className="text-sm">Client</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span className="text-sm">Internal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-500 rounded" />
            <span className="text-sm">Interview</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded" />
            <span className="text-sm">Presentation</span>
          </div>
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-blue-500" />
            <span className="text-sm">AI Prepared</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}