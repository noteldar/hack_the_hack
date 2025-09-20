"use client"

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSocketEvent } from '@/contexts/socket-context'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Bot,
  CheckCircle,
  Clock,
  Mail,
  Calendar,
  X,
  Bell
} from 'lucide-react'

interface Notification {
  id: string
  type: 'agent_activity' | 'task_update' | 'meeting_scheduled' | 'email_processed'
  title: string
  message: string
  timestamp: Date
  read: boolean
  icon: React.ReactNode
  color: string
}

export function NotificationSystem() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showNotifications, setShowNotifications] = useState(false)

  // Listen for real-time events and convert to notifications
  useSocketEvent('agent_activity', (data) => {
    const notification: Notification = {
      id: Math.random().toString(36).substring(7),
      type: 'agent_activity',
      title: `${data.agentName}`,
      message: data.action,
      timestamp: new Date(data.timestamp),
      read: false,
      icon: <Bot className="w-4 h-4" />,
      color: 'bg-purple-500'
    }
    addNotification(notification)
  })

  useSocketEvent('task_update', (data) => {
    const notification: Notification = {
      id: Math.random().toString(36).substring(7),
      type: 'task_update',
      title: 'Task Updated',
      message: `Task progress updated to ${data.progress}% by ${data.agent}`,
      timestamp: new Date(data.timestamp),
      read: false,
      icon: <CheckCircle className="w-4 h-4" />,
      color: 'bg-green-500'
    }
    addNotification(notification)
  })

  useSocketEvent('meeting_scheduled', (data) => {
    const notification: Notification = {
      id: Math.random().toString(36).substring(7),
      type: 'meeting_scheduled',
      title: 'Meeting Scheduled',
      message: `${data.title} scheduled by ${data.scheduledBy}`,
      timestamp: new Date(data.timestamp),
      read: false,
      icon: <Calendar className="w-4 h-4" />,
      color: 'bg-blue-500'
    }
    addNotification(notification)
  })

  useSocketEvent('email_processed', (data) => {
    const notification: Notification = {
      id: Math.random().toString(36).substring(7),
      type: 'email_processed',
      title: 'Email Processed',
      message: `New ${data.priority} priority email from ${data.from}`,
      timestamp: new Date(data.timestamp),
      read: false,
      icon: <Mail className="w-4 h-4" />,
      color: data.priority === 'high' ? 'bg-red-500' : 'bg-blue-500'
    }
    addNotification(notification)
  })

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 10)) // Keep last 10
  }

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    )
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id))
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <>
      {/* Notification Bell */}
      <div className="relative">
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          onClick={() => setShowNotifications(!showNotifications)}
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center"
            >
              <Badge className="bg-red-500 text-white text-xs p-0 w-5 h-5 flex items-center justify-center">
                {unreadCount}
              </Badge>
            </motion.div>
          )}
        </Button>

        {/* Notification Panel */}
        <AnimatePresence>
          {showNotifications && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute right-0 top-full mt-2 w-80 bg-background border border-border rounded-lg shadow-lg z-50"
            >
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Notifications</h3>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowNotifications(false)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-muted-foreground">
                    No notifications yet
                  </div>
                ) : (
                  <div className="divide-y divide-border">
                    {notifications.map((notification) => (
                      <motion.div
                        key={notification.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className={`p-4 hover:bg-muted/50 transition-colors cursor-pointer ${
                          !notification.read ? 'bg-muted/30' : ''
                        }`}
                        onClick={() => markAsRead(notification.id)}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-8 h-8 rounded-full ${notification.color} flex items-center justify-center text-white`}>
                            {notification.icon}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <h4 className={`font-medium text-sm ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                                {notification.title}
                              </h4>
                              <div className="flex items-center gap-2">
                                {!notification.read && (
                                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                                )}
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="w-4 h-4"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    removeNotification(notification.id)
                                  }}
                                >
                                  <X className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                              {notification.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {notifications.length > 0 && (
                <div className="p-4 border-t border-border">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => setNotifications([])}
                  >
                    Clear All
                  </Button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        <AnimatePresence>
          {notifications.slice(0, 3).map((notification) => (
            !notification.read && (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: 300 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 300 }}
                transition={{ duration: 0.3 }}
                className="bg-background border border-border rounded-lg shadow-lg p-4 min-w-72"
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full ${notification.color} flex items-center justify-center text-white shrink-0`}>
                    {notification.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm">{notification.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {notification.message}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-6 h-6 shrink-0"
                    onClick={() => removeNotification(notification.id)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </motion.div>
            )
          ))}
        </AnimatePresence>
      </div>
    </>
  )
}