'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot,
  Brain,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Settings,
  Activity,
  User,
  MessageSquare,
  Zap,
  Target,
  Users,
  Calendar
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { AIStatus } from '@/lib/socket'

interface AIAvatarControlCenterProps {
  personality: 'professional' | 'friendly' | 'direct' | 'analytical'
  onPersonalityChange: (personality: 'professional' | 'friendly' | 'direct' | 'analytical') => void
  aiStatus: AIStatus | null
  connected: boolean
}

const personalityConfigs = {
  professional: {
    name: 'Professional Alex',
    description: 'Formal, diplomatic, structured communication',
    color: 'from-blue-500 to-indigo-500',
    avatar: '👔',
    traits: ['Diplomatic', 'Structured', 'Formal'],
    meetingStyle: 'Takes detailed notes, asks clarifying questions, maintains professional tone'
  },
  friendly: {
    name: 'Friendly Sam',
    description: 'Warm, engaging, collaborative approach',
    color: 'from-green-500 to-emerald-500',
    avatar: '😊',
    traits: ['Collaborative', 'Warm', 'Engaging'],
    meetingStyle: 'Builds rapport, encourages participation, uses casual language'
  },
  direct: {
    name: 'Direct Jordan',
    description: 'Concise, goal-oriented, efficient communication',
    color: 'from-red-500 to-orange-500',
    avatar: '🎯',
    traits: ['Efficient', 'Goal-oriented', 'Concise'],
    meetingStyle: 'Keeps discussions on track, summarizes key points, drives decisions'
  },
  analytical: {
    name: 'Analytical Morgan',
    description: 'Data-driven, logical, detail-oriented analysis',
    color: 'from-purple-500 to-pink-500',
    avatar: '📊',
    traits: ['Data-driven', 'Logical', 'Detail-oriented'],
    meetingStyle: 'Analyzes metrics, provides insights, asks probing questions'
  }
}

const mockMeetingStats = {
  currentMeeting: 'Product Strategy Review',
  duration: '23m',
  participants: 6,
  engagement: 87,
  talkTime: 12,
  insights: 4,
  nextAction: 'Preparing meeting summary...'
}

export function AIAvatarControlCenter({
  personality,
  onPersonalityChange,
  aiStatus,
  connected
}: AIAvatarControlCenterProps) {
  const [isRecording, setIsRecording] = useState(true)
  const [isCameraOn, setIsCameraOn] = useState(false)
  const [activeTab, setActiveTab] = useState('control')

  const currentConfig = personalityConfigs[personality]

  const handlePersonalityChange = (newPersonality: typeof personality) => {
    onPersonalityChange(newPersonality)
  }

  return (
    <Card className="glass-card h-full">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{
                scale: connected ? [1, 1.1, 1] : 1,
                rotate: connected ? [0, 5, -5, 0] : 0
              }}
              transition={{ repeat: connected ? Infinity : 0, duration: 3 }}
            >
              <Bot className="w-5 h-5 text-blue-500" />
            </motion.div>
            <span>AI Avatar Control</span>
          </div>
          <Badge
            variant={connected ? "default" : "secondary"}
            className={connected ? "bg-green-500/10 text-green-600 dark:text-green-400" : ""}
          >
            {connected ? 'Active' : 'Offline'}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="control">Control</TabsTrigger>
            <TabsTrigger value="personality">Avatar</TabsTrigger>
            <TabsTrigger value="meeting">Meeting</TabsTrigger>
          </TabsList>

          <TabsContent value="control" className="space-y-4 mt-4">
            {/* Avatar Status */}
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 border border-gray-200/50 dark:border-gray-700/50">
              <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${currentConfig.color} flex items-center justify-center text-2xl`}>
                {currentConfig.avatar}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">{currentConfig.name}</h3>
                <p className="text-sm text-muted-foreground">
                  {aiStatus?.currentTask || currentConfig.description}
                </p>
              </div>
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            </div>

            {/* Control Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant={isRecording ? "default" : "outline"}
                size="sm"
                onClick={() => setIsRecording(!isRecording)}
                className={isRecording ? "bg-red-500 hover:bg-red-600" : ""}
              >
                {isRecording ? <Mic className="w-4 h-4 mr-2" /> : <MicOff className="w-4 h-4 mr-2" />}
                {isRecording ? 'Recording' : 'Muted'}
              </Button>

              <Button
                variant={isCameraOn ? "default" : "outline"}
                size="sm"
                onClick={() => setIsCameraOn(!isCameraOn)}
                className={isCameraOn ? "bg-blue-500 hover:bg-blue-600" : ""}
              >
                {isCameraOn ? <Video className="w-4 h-4 mr-2" /> : <VideoOff className="w-4 h-4 mr-2" />}
                {isCameraOn ? 'Camera On' : 'Camera Off'}
              </Button>
            </div>

            {/* AI Performance Metrics */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">AI Efficiency</span>
                <span className="font-medium">{aiStatus?.efficiency || 94}%</span>
              </div>
              <Progress value={aiStatus?.efficiency || 94} className="h-2" />

              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Processing Queue</span>
                <span className="font-medium">{aiStatus?.processingMeetings || 0} meetings</span>
              </div>
              <Progress value={((aiStatus?.processingMeetings || 0) / 5) * 100} className="h-2" />
            </div>
          </TabsContent>

          <TabsContent value="personality" className="space-y-4 mt-4">
            {/* Personality Selector */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Avatar Personality</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(personalityConfigs).map(([key, config]) => (
                  <motion.button
                    key={key}
                    onClick={() => handlePersonalityChange(key as typeof personality)}
                    className={`p-3 rounded-xl border-2 transition-all text-left ${
                      personality === key
                        ? 'border-purple-500 bg-purple-500/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center space-x-2 mb-2">
                      <div className={`w-6 h-6 rounded-full bg-gradient-to-r ${config.color} flex items-center justify-center text-sm`}>
                        {config.avatar}
                      </div>
                      <span className="font-medium text-sm">{config.name.split(' ')[1]}</span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {config.description}
                    </p>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Current Personality Details */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/5 to-blue-500/5 border border-purple-500/20">
              <h4 className="font-medium mb-2">Active Configuration</h4>
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1 mb-2">
                  {currentConfig.traits.map((trait) => (
                    <Badge key={trait} variant="outline" className="text-xs">
                      {trait}
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {currentConfig.meetingStyle}
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="meeting" className="space-y-4 mt-4">
            {/* Current Meeting Info */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">Current Meeting</h4>
                <Badge className="bg-green-500/10 text-green-600 dark:text-green-400">
                  Live
                </Badge>
              </div>

              <div className="p-3 rounded-xl bg-gradient-to-r from-green-500/5 to-emerald-500/5 border border-green-500/20">
                <h5 className="font-medium mb-1">{mockMeetingStats.currentMeeting}</h5>
                <p className="text-sm text-muted-foreground mb-2">{mockMeetingStats.nextAction}</p>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Duration:</span>
                    <span className="ml-2 font-medium">{mockMeetingStats.duration}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Participants:</span>
                    <span className="ml-2 font-medium">{mockMeetingStats.participants}</span>
                  </div>
                </div>
              </div>

              {/* Meeting Metrics */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Engagement Score</span>
                  <span className="font-medium">{mockMeetingStats.engagement}%</span>
                </div>
                <Progress value={mockMeetingStats.engagement} className="h-2" />

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">AI Talk Time</span>
                  <span className="font-medium">{mockMeetingStats.talkTime}%</span>
                </div>
                <Progress value={mockMeetingStats.talkTime} className="h-2" />

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Insights Generated</span>
                  <span className="font-medium">{mockMeetingStats.insights}</span>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}