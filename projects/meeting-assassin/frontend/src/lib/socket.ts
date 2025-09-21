import socketIO from 'socket.io-client'
const io = socketIO
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Socket = any

export interface SocketEvents {
  'calendar-update': (data: CalendarUpdate) => void
  'meeting-analysis': (data: MeetingAnalysis) => void
  'ai-status': (data: AIStatus) => void
  'productivity-metrics': (data: ProductivityMetrics) => void
  'optimization-complete': (data: OptimizationResult) => void
  'genetic-algorithm-update': (data: GeneticAlgorithmUpdate) => void
  'avatar-decision': (data: AvatarDecision) => void
  'real-time-savings': (data: RealTimeSavings) => void
}

export interface GeneticAlgorithmUpdate {
  generation: number
  bestFitness: number
  averageFitness: number
  improvements: string[]
  convergence: number
  estimatedCompletion: string
}

export interface AvatarDecision {
  id: string
  type: 'meeting_join' | 'meeting_decline' | 'reschedule' | 'break_suggestion'
  decision: string
  reasoning: string
  confidence: number
  personality: 'professional' | 'friendly' | 'direct' | 'analytical'
  timestamp: string
}

export interface RealTimeSavings {
  totalTimeSaved: number
  sessionTimeSaved: number
  costSavings: number
  efficiencyGain: number
  timestamp: string
}

export interface CalendarUpdate {
  id: string
  type: 'create' | 'update' | 'delete' | 'optimize'
  meeting: {
    id: string
    title: string
    start: string
    end: string
    attendees: string[]
    priority: 'low' | 'medium' | 'high'
    category: 'meeting' | 'focus' | 'break' | 'travel'
  }
  optimization?: {
    originalStart: string
    suggestedStart: string
    reason: string
    confidence: number
  }
}

export interface MeetingAnalysis {
  meetingId: string
  insights: {
    efficiency: number
    engagement: number
    outcomes: string[]
    recommendations: string[]
    timeWasted: number
    productiveTime: number
  }
  participants: {
    id: string
    name: string
    engagement: number
    talkTime: number
  }[]
}

export interface AIStatus {
  status: 'active' | 'idle' | 'processing' | 'error'
  currentTask?: string
  processingMeetings: number
  efficiency: number
  lastUpdate: string
}

export interface ProductivityMetrics {
  daily: {
    focusTime: number
    meetingTime: number
    breakTime: number
    efficiency: number
  }
  weekly: {
    totalHours: number
    productiveHours: number
    meetingHours: number
    focusHours: number
    trend: 'up' | 'down' | 'stable'
  }
  goals: {
    focusTimeGoal: number
    meetingLimitGoal: number
    efficiencyGoal: number
    current: {
      focusTime: number
      meetingCount: number
      efficiency: number
    }
  }
}

export interface OptimizationResult {
  id: string
  type: 'schedule' | 'meeting' | 'calendar'
  before: unknown
  after: unknown
  improvements: {
    timeSaved: number
    efficiencyGain: number
    conflictsResolved: number
  }
  confidence: number
}

class SocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 1000

  connect(url: string = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000') {
    if (this.socket?.connected) {
      return this.socket
    }

    this.socket = io(url, {
      transports: ['websocket'],
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectInterval,
    })

    this.socket.on('connect', () => {
      console.log('Connected to MeetingAssassin AI')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      console.log('Disconnected from MeetingAssassin AI')
    })

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      this.handleReconnect()
    })

    return this.socket
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnection attempt ${this.reconnectAttempts}`)
        this.socket?.connect()
      }, this.reconnectInterval * this.reconnectAttempts)
    }
  }

  emit(event: string, data: unknown) {
    this.socket?.emit(event, data)
  }

  on<K extends keyof SocketEvents>(event: K, handler: SocketEvents[K]) {
    this.socket?.on(event, handler)
  }

  off<K extends keyof SocketEvents>(event: K, handler?: SocketEvents[K]) {
    this.socket?.off(event, handler)
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  get connected() {
    return this.socket?.connected || false
  }

  // Utility methods for common operations
  subscribeToCalendarUpdates(handler: (data: CalendarUpdate) => void) {
    this.on('calendar-update', handler)
    this.emit('subscribe', 'calendar-updates')
  }

  subscribeToMeetingAnalysis(handler: (data: MeetingAnalysis) => void) {
    this.on('meeting-analysis', handler)
    this.emit('subscribe', 'meeting-analysis')
  }

  subscribeToAIStatus(handler: (data: AIStatus) => void) {
    this.on('ai-status', handler)
    this.emit('subscribe', 'ai-status')
  }

  subscribeToProductivityMetrics(handler: (data: ProductivityMetrics) => void) {
    this.on('productivity-metrics', handler)
    this.emit('subscribe', 'productivity-metrics')
  }

  requestCalendarOptimization(preferences: { [key: string]: boolean | { start: string; end: string } }) {
    this.emit('request-optimization', {
      type: 'calendar',
      preferences
    })
  }

  requestMeetingAnalysis(meetingId: string) {
    this.emit('request-analysis', {
      type: 'meeting',
      meetingId
    })
  }

  subscribeToGeneticAlgorithmUpdates(handler: (data: GeneticAlgorithmUpdate) => void) {
    this.on('genetic-algorithm-update', handler)
    this.emit('subscribe', 'genetic-algorithm-updates')
  }

  subscribeToAvatarDecisions(handler: (data: AvatarDecision) => void) {
    this.on('avatar-decision', handler)
    this.emit('subscribe', 'avatar-decisions')
  }

  subscribeToRealTimeSavings(handler: (data: RealTimeSavings) => void) {
    this.on('real-time-savings', handler)
    this.emit('subscribe', 'real-time-savings')
  }

  subscribeToOptimizationResults(handler: (data: OptimizationResult) => void) {
    this.on('optimization-complete', handler)
    this.emit('subscribe', 'optimization-results')
  }

  setAvatarPersonality(personality: 'professional' | 'friendly' | 'direct' | 'analytical') {
    this.emit('set-avatar-personality', { personality })
  }

  requestDemoData() {
    this.emit('request-demo-data')
  }
}

// Singleton instance
const socketClient = new SocketClient()

export default socketClient