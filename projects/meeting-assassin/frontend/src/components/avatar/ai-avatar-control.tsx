'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot,
  Brain,
  Zap,
  Settings,
  Play,
  Pause,
  RotateCcw,
  MessageSquare,
  Calendar,
  Clock,
  Users,
  Target,
  Activity,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  Cpu,
  HardDrive,
  Wifi,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useSocket } from '@/contexts/socket-context'

interface AICapability {
  id: string
  name: string
  description: string
  enabled: boolean
  performance: number
  icon: React.ComponentType<{ className?: string }>
  color: string
}

const aiCapabilities: AICapability[] = [
  {
    id: 'calendar_optimization',
    name: 'Calendar Optimization',
    description: 'Automatically optimize your schedule for maximum productivity',
    enabled: true,
    performance: 94,
    icon: Calendar,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'meeting_analysis',
    name: 'Meeting Analysis',
    description: 'Analyze meeting effectiveness and provide insights',
    enabled: true,
    performance: 87,
    icon: Users,
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'smart_scheduling',
    name: 'Smart Scheduling',
    description: 'Intelligently schedule meetings based on preferences',
    enabled: true,
    performance: 91,
    icon: Clock,
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'email_assistance',
    name: 'Email Assistance',
    description: 'Draft responses and manage email communications',
    enabled: false,
    performance: 78,
    icon: MessageSquare,
    color: 'from-orange-500 to-red-500'
  },
  {
    id: 'productivity_tracking',
    name: 'Productivity Tracking',
    description: 'Monitor and analyze your work patterns',
    enabled: true,
    performance: 96,
    icon: Target,
    color: 'from-indigo-500 to-blue-500'
  }
]

const systemMetrics = {
  cpu: 34,
  memory: 67,
  network: 89,
  uptime: '99.8%',
  responsesProcessed: 1247,
  optimizationsMade: 23,
  timeSaved: '4.2h'
}

export function AIAvatarControl() {
  const { aiStatus, connected } = useSocket()
  const [capabilities, setCapabilities] = useState(aiCapabilities)
  const [aiPersonality, setAIPersonality] = useState({
    assertiveness: [70],
    creativity: [85],
    efficiency: [90],
    communication: [75]
  })
  const [isListening, setIsListening] = useState(true)
  const [isVisible, setIsVisible] = useState(true)
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [autoMode, setAutoMode] = useState(true)

  const toggleCapability = (id: string) => {
    setCapabilities(prev =>
      prev.map(cap =>
        cap.id === id ? { ...cap, enabled: !cap.enabled } : cap
      )
    )
  }

  const handlePersonalityChange = (trait: string, value: number[]) => {
    setAIPersonality(prev => ({
      ...prev,
      [trait]: value
    }))
  }

  const restartAI = () => {
    // Simulate AI restart
    setCapabilities(prev => prev.map(cap => ({ ...cap, performance: 100 })))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
            AI Avatar Control
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage your AI assistant capabilities and behavior
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Badge
            className={`${
              connected
                ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
            }`}
          >
            <div className={`w-2 h-2 rounded-full mr-2 ${
              connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`} />
            {connected ? 'AI Online' : 'AI Offline'}
          </Badge>
        </div>
      </motion.div>

      {/* AI Avatar Visualization */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="glass-card glow-effect">
          <CardContent className="p-8">
            <div className="flex items-center justify-center mb-6">
              <motion.div
                className="relative"
                animate={{
                  scale: connected ? [1, 1.05, 1] : 1,
                  rotate: connected ? [0, 5, -5, 0] : 0
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <div className="w-32 h-32 bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 rounded-full flex items-center justify-center animate-pulse-glow">
                  <Bot className="w-16 h-16 text-white" />
                </div>
                {connected && (
                  <motion.div
                    className="absolute -inset-4 rounded-full border-2 border-purple-400/30"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                  />
                )}
              </motion.div>
            </div>

            <div className="text-center space-y-2 mb-6">
              <h3 className="text-xl font-bold">MeetingAssassin AI</h3>
              <p className="text-muted-foreground">
                {aiStatus?.currentTask || 'Ready to assist with your productivity goals'}
              </p>
              <div className="flex items-center justify-center space-x-4 text-sm">
                <span className="flex items-center space-x-1">
                  <Activity className="w-4 h-4" />
                  <span>Processing {aiStatus?.processingMeetings || 0} meetings</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Target className="w-4 h-4" />
                  <span>{aiStatus?.efficiency || 94}% efficiency</span>
                </span>
              </div>
            </div>

            {/* Quick Controls */}
            <div className="flex items-center justify-center space-x-4">
              <Button
                variant={autoMode ? 'default' : 'outline'}
                onClick={() => setAutoMode(!autoMode)}
                className="flex items-center space-x-2"
              >
                {autoMode ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{autoMode ? 'Auto Mode' : 'Manual Mode'}</span>
              </Button>

              <Button
                variant="outline"
                onClick={restartAI}
                className="flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Restart</span>
              </Button>

              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsListening(!isListening)}
                  className={isListening ? 'text-green-600' : 'text-gray-400'}
                >
                  {isListening ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  className={voiceEnabled ? 'text-blue-600' : 'text-gray-400'}
                >
                  {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Controls */}
      <Tabs defaultValue="capabilities" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
          <TabsTrigger value="personality">Personality</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="capabilities" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {capabilities.map((capability, index) => (
              <motion.div
                key={capability.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className={`glass-card transition-all duration-300 ${
                  capability.enabled
                    ? 'glow-effect border-purple-500/20'
                    : 'opacity-75 grayscale'
                }`}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${capability.color} flex items-center justify-center`}>
                        <capability.icon className="w-6 h-6 text-white" />
                      </div>
                      <Switch
                        checked={capability.enabled}
                        onCheckedChange={() => toggleCapability(capability.id)}
                      />
                    </div>

                    <div className="space-y-3">
                      <div>
                        <h3 className="font-semibold">{capability.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {capability.description}
                        </p>
                      </div>

                      {capability.enabled && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Performance</span>
                            <span className="font-medium">{capability.performance}%</span>
                          </div>
                          <Progress value={capability.performance} className="h-2" />
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="personality" className="space-y-6">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-purple-500" />
                <span>AI Personality Tuning</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
              {Object.entries(aiPersonality).map(([trait, value]) => (
                <motion.div
                  key={trait}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium capitalize">
                      {trait.replace(/([A-Z])/g, ' $1').trim()}
                    </label>
                    <Badge variant="outline">{value[0]}%</Badge>
                  </div>
                  <Slider
                    value={value}
                    onValueChange={(newValue) => handlePersonalityChange(trait, newValue)}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">
                    {trait === 'assertiveness' && 'How proactive the AI is in making suggestions'}
                    {trait === 'creativity' && 'How creative the AI is in finding solutions'}
                    {trait === 'efficiency' && 'How much the AI prioritizes efficiency over other factors'}
                    {trait === 'communication' && 'How frequently the AI communicates with you'}
                  </p>
                </motion.div>
              ))}

              <div className="pt-4 border-t">
                <Button className="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white">
                  Apply Personality Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          {/* System Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Cpu className="w-5 h-5 text-blue-500" />
                    <span className="font-medium">CPU Usage</span>
                  </div>
                  <Badge variant="outline">{systemMetrics.cpu}%</Badge>
                </div>
                <Progress value={systemMetrics.cpu} className="h-2" />
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <HardDrive className="w-5 h-5 text-green-500" />
                    <span className="font-medium">Memory</span>
                  </div>
                  <Badge variant="outline">{systemMetrics.memory}%</Badge>
                </div>
                <Progress value={systemMetrics.memory} className="h-2" />
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Wifi className="w-5 h-5 text-purple-500" />
                    <span className="font-medium">Network</span>
                  </div>
                  <Badge variant="outline">{systemMetrics.network}%</Badge>
                </div>
                <Progress value={systemMetrics.network} className="h-2" />
              </CardContent>
            </Card>
          </div>

          {/* Performance Stats */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-orange-500" />
                <span>Performance Statistics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{systemMetrics.uptime}</div>
                  <div className="text-sm text-muted-foreground">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{systemMetrics.responsesProcessed}</div>
                  <div className="text-sm text-muted-foreground">Responses Processed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{systemMetrics.optimizationsMade}</div>
                  <div className="text-sm text-muted-foreground">Optimizations Today</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{systemMetrics.timeSaved}</div>
                  <div className="text-sm text-muted-foreground">Time Saved Today</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-gray-500" />
                <span>AI Settings</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                {
                  title: 'Auto-optimize Calendar',
                  description: 'Automatically optimize your calendar based on productivity patterns',
                  checked: true
                },
                {
                  title: 'Smart Notifications',
                  description: 'Receive intelligent notifications about schedule conflicts and opportunities',
                  checked: true
                },
                {
                  title: 'Meeting Insights',
                  description: 'Generate insights and recommendations after each meeting',
                  checked: false
                },
                {
                  title: 'Proactive Scheduling',
                  description: 'Allow AI to proactively suggest and schedule meetings',
                  checked: false
                },
                {
                  title: 'Learning Mode',
                  description: 'Continuously learn from your preferences and behaviors',
                  checked: true
                }
              ].map((setting, index) => (
                <motion.div
                  key={setting.title}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50"
                >
                  <div className="flex-1 pr-4">
                    <h4 className="font-medium">{setting.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {setting.description}
                    </p>
                  </div>
                  <Switch defaultChecked={setting.checked} />
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}