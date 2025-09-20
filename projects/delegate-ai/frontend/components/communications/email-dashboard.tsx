"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { formatTime, getTimeAgo } from "@/lib/utils"
import {
  Mail,
  Search,
  Filter,
  Star,
  Archive,
  Trash2,
  Reply,
  Forward,
  Bot,
  Clock,
  AlertCircle,
  CheckCircle,
  Paperclip
} from "lucide-react"

interface Email {
  id: string
  from: {
    name: string
    email: string
    avatar?: string
  }
  subject: string
  preview: string
  timestamp: Date
  read: boolean
  starred: boolean
  hasAttachments: boolean
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category: 'client' | 'internal' | 'vendor' | 'personal' | 'marketing'
  aiStatus: 'pending' | 'drafted' | 'sent' | 'requires_attention'
  aiConfidence?: number
}

const mockEmails: Email[] = [
  {
    id: '1',
    from: {
      name: 'John Smith',
      email: 'john@techcorp.com',
      avatar: '/avatars/john.jpg'
    },
    subject: 'Q4 Budget Review Meeting',
    preview: 'Hi, I wanted to follow up on our discussion about the Q4 budget allocation...',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    read: false,
    starred: true,
    hasAttachments: true,
    priority: 'high',
    category: 'client',
    aiStatus: 'drafted',
    aiConfidence: 92
  },
  {
    id: '2',
    from: {
      name: 'Sarah Wilson',
      email: 'sarah@company.com',
      avatar: '/avatars/sarah.jpg'
    },
    subject: 'Project Alpha Status Update',
    preview: 'The development team has completed the initial phase and we\'re ready to move...',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    read: false,
    starred: false,
    hasAttachments: false,
    priority: 'medium',
    category: 'internal',
    aiStatus: 'sent',
    aiConfidence: 88
  },
  {
    id: '3',
    from: {
      name: 'Mike Johnson',
      email: 'mike@vendor.com',
      avatar: '/avatars/mike.jpg'
    },
    subject: 'Invoice #12345 - Payment Terms',
    preview: 'Thank you for your business. Please find attached the invoice for services...',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    read: true,
    starred: false,
    hasAttachments: true,
    priority: 'medium',
    category: 'vendor',
    aiStatus: 'requires_attention',
    aiConfidence: 65
  },
  {
    id: '4',
    from: {
      name: 'Lisa Chen',
      email: 'lisa@startup.io',
      avatar: '/avatars/lisa.jpg'
    },
    subject: 'Partnership Opportunity',
    preview: 'I hope this email finds you well. I\'m reaching out regarding a potential...',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    read: false,
    starred: false,
    hasAttachments: false,
    priority: 'low',
    category: 'client',
    aiStatus: 'pending',
    aiConfidence: null
  },
  {
    id: '5',
    from: {
      name: 'Marketing Team',
      email: 'marketing@company.com'
    },
    subject: 'Weekly Newsletter - Industry Updates',
    preview: 'Here are this week\'s top industry news and updates that might interest you...',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    read: true,
    starred: false,
    hasAttachments: false,
    priority: 'low',
    category: 'marketing',
    aiStatus: 'sent',
    aiConfidence: 95
  }
]

const getPriorityColor = (priority: Email['priority']) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
    case 'high':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
  }
}

const getCategoryColor = (category: Email['category']) => {
  switch (category) {
    case 'client':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    case 'internal':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100'
    case 'vendor':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100'
    case 'personal':
      return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-100'
    case 'marketing':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
  }
}

const getAIStatusIcon = (status: Email['aiStatus'], confidence?: number) => {
  switch (status) {
    case 'sent':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'drafted':
      return <Bot className="w-4 h-4 text-blue-500" />
    case 'requires_attention':
      return <AlertCircle className="w-4 h-4 text-yellow-500" />
    case 'pending':
      return <Clock className="w-4 h-4 text-gray-500" />
  }
}

function EmailRow({ email }: { email: Email }) {
  return (
    <Card className={`mb-2 transition-all hover:shadow-sm ${
      !email.read ? 'border-l-4 border-l-blue-500 bg-blue-50/30 dark:bg-blue-950/10' : ''
    }`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <Avatar className="w-10 h-10">
            <AvatarImage src={email.from.avatar} alt={email.from.name} />
            <AvatarFallback>
              {email.from.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
            </AvatarFallback>
          </Avatar>

          {/* Email Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <h4 className={`font-medium truncate ${!email.read ? 'font-semibold' : ''}`}>
                  {email.from.name}
                </h4>
                <span className="text-sm text-muted-foreground">
                  {email.from.email}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">
                  {getTimeAgo(email.timestamp)}
                </span>
                {email.starred && <Star className="w-4 h-4 text-yellow-500 fill-current" />}
                {email.hasAttachments && <Paperclip className="w-4 h-4 text-gray-500" />}
              </div>
            </div>

            <h3 className={`text-sm mb-1 truncate ${!email.read ? 'font-semibold' : ''}`}>
              {email.subject}
            </h3>

            <p className="text-sm text-muted-foreground mb-2 line-clamp-1">
              {email.preview}
            </p>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={getPriorityColor(email.priority)}>
                  {email.priority}
                </Badge>
                <Badge variant="outline" className={getCategoryColor(email.category)}>
                  {email.category}
                </Badge>
              </div>

              <div className="flex items-center gap-2">
                {/* AI Status */}
                <div className="flex items-center gap-1">
                  {getAIStatusIcon(email.aiStatus, email.aiConfidence)}
                  <span className="text-xs text-muted-foreground capitalize">
                    {email.aiStatus.replace('_', ' ')}
                  </span>
                  {email.aiConfidence && (
                    <span className="text-xs text-muted-foreground">
                      ({email.aiConfidence}%)
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="w-6 h-6">
                    <Reply className="w-3 h-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="w-6 h-6">
                    <Forward className="w-3 h-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="w-6 h-6">
                    <Archive className="w-3 h-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="w-6 h-6">
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function EmailDashboard() {
  const unreadCount = mockEmails.filter(email => !email.read).length
  const aiDraftedCount = mockEmails.filter(email => email.aiStatus === 'drafted').length
  const requiresAttentionCount = mockEmails.filter(email => email.aiStatus === 'requires_attention').length

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Email List */}
      <div className="lg:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="w-5 h-5" />
                Inbox
                {unreadCount > 0 && (
                  <Badge variant="destructive">{unreadCount}</Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search emails..."
                    className="pl-10 w-64"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-0">
              {mockEmails.map((email) => (
                <EmailRow key={email.id} email={email} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* AI Status */}
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
              <Bot className="w-5 h-5" />
              AI Assistant
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Drafts Ready</span>
              <Badge className="bg-blue-600">{aiDraftedCount}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Needs Attention</span>
              <Badge variant="destructive">{requiresAttentionCount}</Badge>
            </div>
            <Button className="w-full" size="sm">
              <Bot className="w-4 h-4 mr-2" />
              Review Drafts
            </Button>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start" size="sm">
              <CheckCircle className="w-4 h-4 mr-2" />
              Mark All Read
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Archive className="w-4 h-4 mr-2" />
              Archive Old
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Bot className="w-4 h-4 mr-2" />
              Auto-Process
            </Button>
          </CardContent>
        </Card>

        {/* Categories */}
        <Card>
          <CardHeader>
            <CardTitle>Categories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {['client', 'internal', 'vendor', 'personal', 'marketing'].map((category) => {
              const count = mockEmails.filter(e => e.category === category).length
              return (
                <div key={category} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{category}</span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              )
            })}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}