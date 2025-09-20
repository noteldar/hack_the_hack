"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  TrendingUp,
  Clock,
  CheckCircle,
  Mail,
  Calendar,
  Target
} from "lucide-react"

interface Metric {
  title: string
  value: string | number
  change: number
  period: string
  icon: React.ReactNode
  color: string
}

const metrics: Metric[] = [
  {
    title: "Tasks Completed",
    value: 47,
    change: 12,
    period: "this week",
    icon: <CheckCircle className="w-5 h-5" />,
    color: "text-green-600"
  },
  {
    title: "Time Saved",
    value: "8.2h",
    change: 15,
    period: "today",
    icon: <Clock className="w-5 h-5" />,
    color: "text-blue-600"
  },
  {
    title: "Emails Handled",
    value: 134,
    change: 8,
    period: "today",
    icon: <Mail className="w-5 h-5" />,
    color: "text-purple-600"
  },
  {
    title: "Meetings Optimized",
    value: 23,
    change: 18,
    period: "this week",
    icon: <Calendar className="w-5 h-5" />,
    color: "text-orange-600"
  }
]

const goalProgress = [
  {
    label: "Weekly Task Goal",
    current: 47,
    target: 60,
    color: "bg-green-500"
  },
  {
    label: "Email Response Time",
    current: 85,
    target: 100,
    color: "bg-blue-500"
  },
  {
    label: "Meeting Efficiency",
    current: 92,
    target: 100,
    color: "bg-purple-500"
  }
]

export function ProductivityMetrics() {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <Card key={metric.title} className="relative overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className={metric.color}>
                  {metric.icon}
                </div>
                <Badge
                  variant="secondary"
                  className={`${
                    metric.change > 0
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100"
                  }`}
                >
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {metric.change > 0 ? "+" : ""}{metric.change}%
                </Badge>
              </div>
              <div className="mt-4">
                <div className="text-2xl font-bold">
                  {metric.value}
                </div>
                <div className="text-sm text-muted-foreground">
                  {metric.title}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  vs {metric.period}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Goal Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Goal Progress
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {goalProgress.map((goal) => (
            <div key={goal.label} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{goal.label}</span>
                <span className="text-muted-foreground">
                  {goal.current}/{goal.target}
                  {goal.label.includes("Time") ? "%" : ""}
                </span>
              </div>
              <Progress
                value={(goal.current / goal.target) * 100}
                className="h-2"
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>
                  {Math.round((goal.current / goal.target) * 100)}% complete
                </span>
                <span>
                  {goal.target - goal.current} to go
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* AI Insights */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
            <TrendingUp className="w-5 h-5" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Peak productivity</strong> detected between 9-11 AM. Consider scheduling important tasks during this window.
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Email efficiency up 15%</strong> this week thanks to automated responses and smart filtering.
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2" />
              <p className="text-sm">
                <strong>Meeting optimization</strong> saved 2.5 hours by consolidating related discussions.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}