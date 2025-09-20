import { io, Socket } from 'socket.io-client'

class SocketService {
  private socket: Socket | null = null
  private isConnected = false

  connect() {
    if (this.socket?.connected) return this.socket

    // In a real application, this would connect to your backend
    // For demo purposes, we'll simulate socket events
    this.socket = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001', {
      transports: ['websocket'],
      autoConnect: false
    })

    this.socket.on('connect', () => {
      this.isConnected = true
      console.log('Socket connected')
    })

    this.socket.on('disconnect', () => {
      this.isConnected = false
      console.log('Socket disconnected')
    })

    this.socket.on('error', (error) => {
      console.error('Socket error:', error)
    })

    this.socket.connect()
    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
    }
  }

  emit(event: string, data: any) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data)
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event: string, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  get connected() {
    return this.isConnected && this.socket?.connected
  }
}

export const socketService = new SocketService()

// Mock socket events for demo purposes
export function startMockSocketEvents() {
  // Simulate real-time agent activities
  const mockEvents = [
    {
      type: 'agent_activity',
      data: {
        agentId: '1',
        agentName: 'Communication Agent',
        action: 'Email response generated',
        timestamp: new Date(),
        details: { emailSubject: 'Client Inquiry', confidence: 92 }
      }
    },
    {
      type: 'task_update',
      data: {
        taskId: '1',
        status: 'in_progress',
        progress: 75,
        agent: 'Task Manager',
        timestamp: new Date()
      }
    },
    {
      type: 'meeting_scheduled',
      data: {
        meetingId: '1',
        title: 'Client Review Meeting',
        scheduledBy: 'Calendar Agent',
        timestamp: new Date()
      }
    },
    {
      type: 'email_processed',
      data: {
        from: 'client@example.com',
        subject: 'Project Update',
        category: 'client',
        priority: 'high',
        timestamp: new Date()
      }
    }
  ]

  // Emit mock events at intervals
  let eventIndex = 0
  setInterval(() => {
    const event = mockEvents[eventIndex % mockEvents.length]

    // Simulate broadcasting the event
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('socket-event', {
        detail: event
      }))
    }

    eventIndex++
  }, 5000) // Every 5 seconds
}

export default socketService