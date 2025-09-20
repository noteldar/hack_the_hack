"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ActivityFeed } from "./activity-feed"
import { ProductivityMetrics } from "./productivity-metrics"
import { AgentStatusGrid } from "./agent-status-grid"
import { ScheduleOverview } from "./schedule-overview"
import {
  Brain,
  Zap,
  TrendingUp,
  Settings,
  RefreshCw,
  MoreHorizontal
} from "lucide-react"

export function DashboardOverview() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Your AI-powered autonomous assistant is managing your workflow
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-muted-foreground">All Systems Active</span>
          </div>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4 mr-2" />
            Configure
          </Button>
        </div>
      </div>

      {/* AI Status Banner */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">
                  AI Chief of Staff Active
                </h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  6 agents working autonomously • Processing 12 active tasks
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">+15% efficiency</span>
                </div>
                <p className="text-xs text-muted-foreground">vs last week</p>
              </div>
              <Button variant="secondary" size="sm" className="bg-white/50 hover:bg-white/70">
                <Zap className="w-4 h-4 mr-2" />
                Optimize
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Activity Feed */}
        <ActivityFeed />

        {/* Middle Column - Schedule */}
        <ScheduleOverview />

        {/* Right Column - Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Quick Actions
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <Brain className="w-4 h-4 mr-2" />
              Ask AI Assistant
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Zap className="w-4 h-4 mr-2" />
              Delegate New Task
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Configure Agents
            </Button>

            <div className="pt-3 border-t border-border">
              <h4 className="font-medium text-sm mb-2">Recent Suggestions</h4>
              <div className="space-y-2">
                <div className="p-2 rounded-md bg-muted/50 text-sm">
                  💡 Schedule focused work time between meetings
                </div>
                <div className="p-2 rounded-md bg-muted/50 text-sm">
                  📧 Auto-respond to routine client inquiries
                </div>
                <div className="p-2 rounded-md bg-muted/50 text-sm">
                  📅 Consolidate similar meetings this week
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Status and Metrics Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <AgentStatusGrid />
        <div className="xl:col-span-1">
          <ProductivityMetrics />
        </div>
      </div>
    </div>
  )
}