"use client"

import { motion } from "framer-motion"
import { Progress } from "@/components/ui/progress"
import { useEffect, useState } from "react"

interface AnimatedProgressProps {
  value: number
  className?: string
  duration?: number
  delay?: number
}

export function AnimatedProgress({
  value,
  className,
  duration = 1,
  delay = 0
}: AnimatedProgressProps) {
  const [animatedValue, setAnimatedValue] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(value)
    }, delay * 1000)

    return () => clearTimeout(timer)
  }, [value, delay])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay }}
    >
      <Progress value={animatedValue} className={className} />
      <motion.div
        className="mt-1 text-right"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + duration * 0.5 }}
      >
        <motion.span
          className="text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + duration * 0.8 }}
        >
          {Math.round(animatedValue)}%
        </motion.span>
      </motion.div>
    </motion.div>
  )
}

interface CountUpProps {
  end: number
  start?: number
  duration?: number
  delay?: number
  suffix?: string
  prefix?: string
  className?: string
}

export function CountUp({
  end,
  start = 0,
  duration = 2,
  delay = 0,
  suffix = '',
  prefix = '',
  className
}: CountUpProps) {
  const [count, setCount] = useState(start)

  useEffect(() => {
    let startTime: number
    let animationFrame: number

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime

      const elapsed = currentTime - startTime - delay * 1000
      if (elapsed < 0) {
        animationFrame = requestAnimationFrame(animate)
        return
      }

      const progress = Math.min(elapsed / (duration * 1000), 1)
      const easeOutCubic = 1 - Math.pow(1 - progress, 3)
      const currentCount = Math.round(start + (end - start) * easeOutCubic)

      setCount(currentCount)

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)

    return () => cancelAnimationFrame(animationFrame)
  }, [end, start, duration, delay])

  return (
    <motion.span
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay }}
    >
      {prefix}{count}{suffix}
    </motion.span>
  )
}

export function ProgressRing({
  progress,
  size = 60,
  strokeWidth = 4,
  className
}: {
  progress: number
  size?: number
  strokeWidth?: number
  className?: string
}) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDasharray = `${circumference} ${circumference}`
  const strokeDashoffset = circumference - (progress / 100) * circumference

  return (
    <div className={`relative ${className}`}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-gray-200 dark:text-gray-700"
        />

        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          className="text-blue-500"
          style={{
            strokeDasharray,
          }}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{
            duration: 1,
            ease: "easeOut"
          }}
        />
      </svg>

      {/* Progress text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <CountUp end={progress} suffix="%" className="text-sm font-medium" />
      </div>
    </div>
  )
}