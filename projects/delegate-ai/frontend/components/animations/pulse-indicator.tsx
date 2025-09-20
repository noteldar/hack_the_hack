"use client"

import { motion } from "framer-motion"

interface PulseIndicatorProps {
  color?: string
  size?: 'sm' | 'md' | 'lg'
  speed?: number
}

export function PulseIndicator({
  color = 'bg-green-500',
  size = 'md',
  speed = 1
}: PulseIndicatorProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  return (
    <div className="relative flex items-center justify-center">
      {/* Outer pulse ring */}
      <motion.div
        className={`absolute rounded-full ${color} opacity-20`}
        animate={{
          scale: [1, 1.5, 1],
          opacity: [0.2, 0, 0.2]
        }}
        transition={{
          duration: 2 / speed,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        style={{
          width: size === 'sm' ? '12px' : size === 'md' ? '18px' : '24px',
          height: size === 'sm' ? '12px' : size === 'md' ? '18px' : '24px'
        }}
      />

      {/* Inner dot */}
      <motion.div
        className={`${sizeClasses[size]} rounded-full ${color}`}
        animate={{
          scale: [0.8, 1, 0.8]
        }}
        transition={{
          duration: 1.5 / speed,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  )
}

export function StatusIndicator({
  status,
  size = 'md'
}: {
  status: 'active' | 'idle' | 'processing' | 'offline' | 'error'
  size?: 'sm' | 'md' | 'lg'
}) {
  const statusColors = {
    active: 'bg-green-500',
    processing: 'bg-blue-500',
    idle: 'bg-yellow-500',
    offline: 'bg-gray-500',
    error: 'bg-red-500'
  }

  const isAnimated = status === 'active' || status === 'processing'

  if (isAnimated) {
    return (
      <PulseIndicator
        color={statusColors[status]}
        size={size}
        speed={status === 'processing' ? 1.5 : 1}
      />
    )
  }

  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  return (
    <div className={`${sizeClasses[size]} rounded-full ${statusColors[status]}`} />
  )
}