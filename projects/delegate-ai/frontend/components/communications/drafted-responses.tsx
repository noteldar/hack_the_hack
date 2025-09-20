"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Textarea } from "@/components/ui/textarea"
import { getTimeAgo } from "@/lib/utils"
import {
  Bot,
  Send,
  Edit,
  Trash2,
  Check,
  X,
  ThumbsUp,
  ThumbsDown,
  Eye,
  Clock
} from "lucide-react"

interface DraftedResponse {
  id: string
  originalEmail: {
    from: string
    subject: string
    preview: string
    timestamp: Date
  }
  draftedContent: string
  tone: 'professional' | 'friendly' | 'formal' | 'casual'
  confidence: number
  aiReasoning: string
  status: 'pending_review' | 'approved' | 'needs_revision' | 'rejected'
  generatedAt: Date
}

const mockDrafts: DraftedResponse[] = [
  {
    id: '1',
    originalEmail: {
      from: 'John Smith (TechCorp)',
      subject: 'Q4 Budget Review Meeting',
      preview: 'Hi, I wanted to follow up on our discussion about the Q4 budget allocation...',
      timestamp: new Date(Date.now() - 15 * 60 * 1000)
    },
    draftedContent: `Hi John,

Thank you for following up on the Q4 budget discussion. I've reviewed the allocation proposal and have prepared the quarterly budget analysis.

Based on our conversation, I've identified the key areas where we can optimize spending while maintaining project momentum. The proposed budget reallocation aligns well with our strategic objectives.

I'd be happy to schedule a meeting this week to review the details and finalize the budget plan. Please let me know your availability for Tuesday or Wednesday afternoon.

Best regards,`,
    tone: 'professional',
    confidence: 92,
    aiReasoning: 'Based on previous email patterns, this client prefers concise, professional responses with clear next steps. The tone matches the urgency implied by the "follow up" request.',
    status: 'pending_review',
    generatedAt: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: '2',
    originalEmail: {
      from: 'Lisa Chen (Startup.io)',
      subject: 'Partnership Opportunity',
      preview: 'I hope this email finds you well. I\'m reaching out regarding a potential...',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000)
    },
    draftedContent: `Hi Lisa,

Thank you for reaching out about the partnership opportunity. Your timing is excellent as we're actively exploring strategic collaborations in this space.

I'd love to learn more about your proposal and discuss how our companies might work together. The initial concept you've outlined sounds very promising and aligns with our current growth initiatives.

Would you be available for a brief call next week to explore this further? I'm free Tuesday through Thursday between 2-4 PM EST.

Looking forward to hearing from you.

Best,`,
    tone: 'friendly',
    confidence: 88,
    aiReasoning: 'New contact from a startup suggests a more approachable, friendly tone while maintaining professionalism. The response expresses genuine interest while proposing concrete next steps.',
    status: 'approved',
    generatedAt: new Date(Date.now() - 30 * 60 * 1000)
  },
  {
    id: '3',
    originalEmail: {
      from: 'Mike Johnson (Vendor)',
      subject: 'Invoice #12345 - Payment Terms',
      preview: 'Thank you for your business. Please find attached the invoice for services...',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
    },
    draftedContent: `Hi Mike,

Thank you for sending the invoice. I've received it and am processing the payment according to our standard 30-day terms.

The invoice will be processed by our accounting team and payment should be issued by [date]. You should receive payment confirmation via email once processed.

If you have any questions about the payment timeline or need any additional documentation, please don't hesitate to reach out.

Best regards,`,
    tone: 'professional',
    confidence: 65,
    aiReasoning: 'Standard vendor communication requires formal tone. Low confidence due to lack of specific payment date information that may need manual input.',
    status: 'needs_revision',
    generatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000)
  }
]

const getToneColor = (tone: DraftedResponse['tone']) => {
  switch (tone) {
    case 'professional':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    case 'friendly':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'formal':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100'
    case 'casual':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
  }
}

const getStatusColor = (status: DraftedResponse['status']) => {
  switch (status) {
    case 'pending_review':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
    case 'approved':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'needs_revision':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100'
    case 'rejected':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
  }
}

function DraftCard({ draft }: { draft: DraftedResponse }) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-blue-100 text-blue-700">
                  <Bot className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h4 className="font-medium">AI Response Draft</h4>
                <p className="text-xs text-muted-foreground">
                  Generated {getTimeAgo(draft.generatedAt)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className={getStatusColor(draft.status)}>
                {draft.status.replace('_', ' ')}
              </Badge>
              <Badge variant="outline" className={getToneColor(draft.tone)}>
                {draft.tone}
              </Badge>
              <Badge variant="outline" className="bg-gray-100 text-gray-800">
                {draft.confidence}% confidence
              </Badge>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="w-8 h-8">
              <Eye className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" className="w-8 h-8">
              <Edit className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Original Email Context */}
        <div className="p-3 bg-muted/50 rounded-lg">
          <h5 className="font-medium text-sm mb-1">Responding to:</h5>
          <p className="text-sm font-medium">{draft.originalEmail.subject}</p>
          <p className="text-xs text-muted-foreground">
            From: {draft.originalEmail.from} • {getTimeAgo(draft.originalEmail.timestamp)}
          </p>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {draft.originalEmail.preview}
          </p>
        </div>

        {/* AI Reasoning */}
        <div className="p-3 bg-blue-50/50 dark:bg-blue-950/20 rounded-lg border-l-4 border-blue-200">
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
              AI Reasoning
            </span>
          </div>
          <p className="text-xs text-blue-700 dark:text-blue-300">
            {draft.aiReasoning}
          </p>
        </div>

        {/* Draft Content */}
        <div>
          <h5 className="font-medium text-sm mb-2">Drafted Response:</h5>
          <div className="relative">
            <Textarea
              value={draft.draftedContent}
              readOnly={draft.status === 'approved'}
              className="min-h-32 resize-none"
            />
            {draft.status === 'approved' && (
              <div className="absolute top-2 right-2">
                <Badge className="bg-green-600">
                  <Check className="w-3 h-3 mr-1" />
                  Approved
                </Badge>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm">
              <ThumbsUp className="w-4 h-4 mr-2" />
              Good
            </Button>
            <Button variant="ghost" size="sm">
              <ThumbsDown className="w-4 h-4 mr-2" />
              Needs Work
            </Button>
          </div>

          <div className="flex items-center gap-2">
            {draft.status === 'pending_review' && (
              <>
                <Button variant="outline" size="sm">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </Button>
                <Button size="sm">
                  <Send className="w-4 h-4 mr-2" />
                  Send
                </Button>
              </>
            )}
            {draft.status === 'needs_revision' && (
              <Button size="sm">
                <Bot className="w-4 h-4 mr-2" />
                Regenerate
              </Button>
            )}
            {draft.status === 'approved' && (
              <Button size="sm">
                <Send className="w-4 h-4 mr-2" />
                Send Now
              </Button>
            )}
            <Button variant="ghost" size="sm">
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function DraftedResponses() {
  const pendingCount = mockDrafts.filter(d => d.status === 'pending_review').length
  const approvedCount = mockDrafts.filter(d => d.status === 'approved').length
  const needsRevisionCount = mockDrafts.filter(d => d.status === 'needs_revision').length

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Drafted Responses */}
      <div className="lg:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                AI Drafted Responses
                <Badge variant="secondary">{mockDrafts.length}</Badge>
              </div>
              <Button>
                <Bot className="w-4 h-4 mr-2" />
                Generate More
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {mockDrafts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Bot className="w-12 h-12 mx-auto mb-4 text-blue-500" />
                <p>No drafted responses yet.</p>
                <p className="text-sm">AI will generate responses as new emails arrive.</p>
              </div>
            ) : (
              <div className="space-y-0">
                {mockDrafts.map((draft) => (
                  <DraftCard key={draft.id} draft={draft} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Review Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Pending Review</span>
              <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                {pendingCount}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Approved</span>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                {approvedCount}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Needs Revision</span>
              <Badge variant="outline" className="bg-orange-100 text-orange-800">
                {needsRevisionCount}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Bulk Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Bulk Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Check className="w-4 h-4 mr-2" />
              Approve All
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Send className="w-4 h-4 mr-2" />
              Send Approved
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Bot className="w-4 h-4 mr-2" />
              Regenerate Low Confidence
            </Button>
          </CardContent>
        </Card>

        {/* AI Settings */}
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
              <Bot className="w-5 h-5" />
              AI Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Auto-approve above</span>
                <Badge variant="outline">95% confidence</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Default tone</span>
                <Badge variant="outline">Professional</Badge>
              </div>
            </div>
            <Button variant="outline" className="w-full" size="sm">
              Configure AI
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}