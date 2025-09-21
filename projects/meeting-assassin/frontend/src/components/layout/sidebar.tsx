'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  BarChart3,
  Bot,
  Home,
  Settings,
  Zap,
  Menu,
  X,
  Clock,
  Target,
  Brain
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
    color: 'text-blue-500',
    description: 'Overview & insights'
  },
  {
    name: 'Calendar Optimizer',
    href: '/calendar',
    icon: Calendar,
    color: 'text-green-500',
    description: 'Smart scheduling'
  },
  {
    name: 'Meeting Analysis',
    href: '/meetings',
    icon: BarChart3,
    color: 'text-purple-500',
    description: 'Meeting insights'
  },
  {
    name: 'AI Avatar',
    href: '/avatar',
    icon: Bot,
    color: 'text-orange-500',
    description: 'AI assistant control'
  },
  {
    name: 'Productivity',
    href: '/productivity',
    icon: Zap,
    color: 'text-yellow-500',
    description: 'Performance metrics'
  },
  {
    name: 'Time Tracking',
    href: '/time',
    icon: Clock,
    color: 'text-indigo-500',
    description: 'Time management'
  },
]

const quickActions = [
  { name: 'Focus Mode', icon: Target, color: 'text-red-500' },
  { name: 'AI Insights', icon: Brain, color: 'text-cyan-500' },
]

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: isOpen ? 0 : -300 }}
          transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          className={cn(
            "fixed top-0 left-0 z-50 h-full w-80 glass-card border-r lg:translate-x-0 lg:static lg:z-auto",
            "lg:block"
          )}
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center animate-pulse-glow">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    MeetingAssassin
                  </h1>
                  <p className="text-xs text-muted-foreground">AI Productivity Agent</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setIsOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-6 space-y-2">
              <div className="space-y-1">
                {navigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <motion.div
                      key={item.name}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Link
                        href={item.href}
                        onClick={() => setIsOpen(false)}
                        className={cn(
                          "group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200",
                          isActive
                            ? "bg-gradient-to-r from-purple-500/10 to-blue-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20"
                            : "text-gray-600 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-gray-100"
                        )}
                      >
                        <item.icon
                          className={cn(
                            "mr-3 h-5 w-5 transition-colors",
                            isActive ? item.color : "group-hover:" + item.color
                          )}
                        />
                        <div className="flex-1">
                          <div className="font-medium">{item.name}</div>
                          <div className="text-xs text-muted-foreground mt-0.5">
                            {item.description}
                          </div>
                        </div>
                        {isActive && (
                          <motion.div
                            layoutId="active-tab"
                            className="w-2 h-2 bg-purple-500 rounded-full"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                          />
                        )}
                      </Link>
                    </motion.div>
                  )
                })}
              </div>

              {/* Quick Actions */}
              <div className="mt-8">
                <h3 className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  Quick Actions
                </h3>
                <div className="space-y-1">
                  {quickActions.map((action) => (
                    <motion.button
                      key={action.name}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full flex items-center px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors group"
                    >
                      <action.icon className={cn("mr-3 h-4 w-4", action.color)} />
                      {action.name}
                    </motion.button>
                  ))}
                </div>
              </div>
            </nav>

            {/* Footer */}
            <div className="p-6 border-t border-white/10">
              <div className="glass-card rounded-xl p-4 bg-gradient-to-r from-purple-500/5 to-blue-500/5">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium">AI Status</div>
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
                    <span className="text-xs text-green-600 dark:text-green-400">Active</span>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground">
                  Processing 3 meetings • 94% efficiency
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </>
  )
}