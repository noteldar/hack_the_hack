"use client"

import { motion, AnimatePresence } from "framer-motion"
import { ReactNode } from "react"

interface AnimatedWrapperProps {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'fade'
}

const variants = {
  up: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 }
  },
  down: {
    initial: { y: -20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: 20, opacity: 0 }
  },
  left: {
    initial: { x: 20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -20, opacity: 0 }
  },
  right: {
    initial: { x: -20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 20, opacity: 0 }
  },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  }
}

export function AnimatedWrapper({
  children,
  className,
  delay = 0,
  duration = 0.5,
  direction = 'up'
}: AnimatedWrapperProps) {
  return (
    <motion.div
      className={className}
      initial={variants[direction].initial}
      animate={variants[direction].animate}
      exit={variants[direction].exit}
      transition={{
        duration,
        delay,
        ease: "easeOut"
      }}
    >
      {children}
    </motion.div>
  )
}

export function StaggeredChildren({
  children,
  className,
  staggerDelay = 0.1,
  direction = 'up'
}: {
  children: ReactNode[]
  className?: string
  staggerDelay?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'fade'
}) {
  return (
    <div className={className}>
      {children.map((child, index) => (
        <AnimatedWrapper
          key={index}
          delay={index * staggerDelay}
          direction={direction}
        >
          {child}
        </AnimatedWrapper>
      ))}
    </div>
  )
}

export function FadeInOut({
  children,
  isVisible,
  className
}: {
  children: ReactNode
  isVisible: boolean
  className?: string
}) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={className}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export function SlideIn({
  children,
  direction = 'right',
  className
}: {
  children: ReactNode
  direction?: 'up' | 'down' | 'left' | 'right'
  className?: string
}) {
  const slideVariants = {
    up: { y: '100%' },
    down: { y: '-100%' },
    left: { x: '100%' },
    right: { x: '-100%' }
  }

  return (
    <motion.div
      className={className}
      initial={slideVariants[direction]}
      animate={{ x: 0, y: 0 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 30
      }}
    >
      {children}
    </motion.div>
  )
}

export function ScaleIn({
  children,
  className,
  delay = 0
}: {
  children: ReactNode
  className?: string
  delay?: number
}) {
  return (
    <motion.div
      className={className}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 25,
        delay
      }}
    >
      {children}
    </motion.div>
  )
}