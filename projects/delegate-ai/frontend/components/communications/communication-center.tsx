"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EmailDashboard } from "./email-dashboard"
import { DraftedResponses } from "./drafted-responses"
import { CommunicationTimeline } from "./communication-timeline"
import {
  Mail,
  MessageSquare,
  Send,
  Bot,
  Clock,
  CheckCircle,
  TrendingUp,
  Users
} from "lucide-react"

interface CommunicationStats {
  emailsProcessed: number
  responsesGenerated: number
  avgResponseTime: number
  satisfactionScore: number
}

const mockStats: CommunicationStats = {
  emailsProcessed: 127,
  responsesGenerated: 89,
  avgResponseTime: 4.2, // minutes
  satisfactionScore: 94 // percentage
}

export function CommunicationCenter() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Communication Center</h1>
          <p className="text-muted-foreground mt-1">
            AI-powered email management and automated responses
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button>
            <Send className="w-4 h-4 mr-2" />
            Compose
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Emails Processed</p>
                <p className="text-2xl font-bold">{mockStats.emailsProcessed}</p>
                <p className="text-xs text-green-600 mt-1">+23% from yesterday</p>
              </div>
              <Mail className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">AI Responses</p>
                <p className="text-2xl font-bold">{mockStats.responsesGenerated}</p>
                <p className="text-xs text-green-600 mt-1">70% auto-handled</p>
              </div>
              <Bot className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Response Time</p>
                <p className="text-2xl font-bold">{mockStats.avgResponseTime}m</p>
                <p className="text-xs text-green-600 mt-1">-45% improvement</p>
              </div>
              <Clock className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Satisfaction Score</p>
                <p className="text-2xl font-bold">{mockStats.satisfactionScore}%</p>
                <p className="text-xs text-green-600 mt-1">+8% this week</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Communication Assistant Banner */}
      <Card className="bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-950/20 dark:to-teal-950/20 border-green-200 dark:border-green-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold text-green-900 dark:text-green-100">
                  AI Communication Assistant Active
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Processing inbox • Drafting responses • Learning communication patterns
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">89 drafts ready</span>
                </div>
                <p className="text-xs text-muted-foreground">for review</p>
              </div>
              <Button variant="secondary" size="sm" className="bg-white/50 hover:bg-white/70">
                <Bot className="w-4 h-4 mr-2" />
                Configure
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="inbox" className="space-y-6">
        <TabsList>
          <TabsTrigger value="inbox">Email Dashboard</TabsTrigger>
          <TabsTrigger value="drafts">Drafted Responses</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="inbox">
          <EmailDashboard />
        </TabsContent>

        <TabsContent value="drafts">
          <DraftedResponses />
        </TabsContent>

        <TabsContent value="timeline">
          <CommunicationTimeline />
        </TabsContent>
      </Tabs>
    </div>
  )
}