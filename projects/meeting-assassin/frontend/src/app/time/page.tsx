'use client'

import { motion } from 'framer-motion'
import { Clock, Play, Pause, Square, Timer } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function TimeTrackingPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          Time Tracking
        </h1>
        <p className="text-muted-foreground mt-2">
          Monitor your time allocation and productivity patterns
        </p>
      </motion.div>

      {/* Active Timer */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="glass-card glow-effect max-w-2xl mx-auto">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="text-6xl font-mono font-bold mb-4">
                02:34:15
              </div>
              <Badge className="bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400">
                <Timer className="w-3 h-3 mr-1" />
                Deep Work Session
              </Badge>
            </div>

            <div className="flex items-center justify-center space-x-4">
              <Button className="bg-green-500 hover:bg-green-600 text-white">
                <Play className="w-4 h-4 mr-2" />
                Start
              </Button>
              <Button variant="outline">
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </Button>
              <Button variant="outline">
                <Square className="w-4 h-4 mr-2" />
                Stop
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Coming Soon */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="text-center py-12"
      >
        <div className="max-w-md mx-auto">
          <Clock className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-xl font-semibold mb-2">Advanced Time Tracking Coming Soon</h3>
          <p className="text-muted-foreground">
            Detailed time analytics, project tracking, and AI-powered insights are in development.
          </p>
        </div>
      </motion.div>
    </div>
  )
}