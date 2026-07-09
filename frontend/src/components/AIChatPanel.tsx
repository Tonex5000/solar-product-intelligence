import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  Bot, 
  User, 
  Sparkles,
  Loader2,
  ChevronDown,
  AlertCircle,
  MessageSquare
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSimulationStore } from '@/stores/simulationStore'
import type { ExplanationLevel } from '@/types'

const explanationLevels: { value: ExplanationLevel; label: string }[] = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'engineer', label: 'Engineer' },
]

const quickQuestions = [
  'Why did my battery degrade?',
  'What caused the warnings?',
  'How can I improve efficiency?',
  'Is my inverter undersized?',
]

export function AIChatPanel() {
  const { chatMessages, addChatMessage } = useSimulationStore()
  const [input, setInput] = useState('')
  const [level, setLevel] = useState<ExplanationLevel>('intermediate')
  const [isLoading, setIsLoading] = useState(false)
  const [showQuickQuestions, setShowQuickQuestions] = useState(true)

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: input,
      timestamp: new Date(),
    }

    addChatMessage(userMessage)
    setInput('')
    setIsLoading(true)
    setShowQuickQuestions(false)

    // Simulate AI response
    await new Promise(resolve => setTimeout(resolve, 1500))

    const aiResponse = {
      id: (Date.now() + 1).toString(),
      role: 'assistant' as const,
      content: `Based on the simulation data, here's my analysis:\n\n**Key Finding:** Your battery degradation is primarily due to operating at high Depth of Discharge (DoD) levels exceeding 80%.\n\n**Recommendations:**\n1. Reduce daily DoD to 50% or below\n2. Consider upgrading to a larger capacity battery\n3. Add solar panels to increase charging capacity\n\nWould you like me to explain any of these factors in more detail?`,
      timestamp: new Date(),
    }

    addChatMessage(aiResponse)
    setIsLoading(false)
  }

  const handleQuickQuestion = (question: string) => {
    setInput(question)
  }

  return (
    <div className="glass-card rounded-2xl h-[calc(100vh-200px)] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-solar-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-solar flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold">AI Assistant</h3>
            <p className="text-xs text-muted-foreground">Powered by SolarFlow AI</p>
          </div>
        </div>

        {/* Level Selector */}
        <div className="flex gap-2">
          {explanationLevels.map((l) => (
            <button
              key={l.value}
              onClick={() => setLevel(l.value)}
              className={cn(
                'flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                level === l.value
                  ? 'bg-primary text-white'
                  : 'bg-solar-bg-card text-muted-foreground hover:text-foreground'
              )}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.length === 0 && !showQuickQuestions && (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
            <p className="text-muted-foreground">Ask me anything about your simulation</p>
          </div>
        )}

        {/* Quick Questions */}
        {showQuickQuestions && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground mb-3">Suggested questions:</p>
            {quickQuestions.map((question, index) => (
              <motion.button
                key={question}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => handleQuickQuestion(question)}
                className="w-full text-left p-3 rounded-xl bg-solar-bg-card hover:bg-primary/10 border border-solar-border hover:border-primary/30 transition-all text-sm"
              >
                {question}
              </motion.button>
            ))}
          </div>
        )}

        {/* Chat Messages */}
        {chatMessages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              'ai-chat-bubble rounded-2xl p-4',
              message.role === 'user' ? 'ai-chat-bubble-user ml-auto' : 'ai-chat-bubble-ai'
            )}
          >
            <div className="flex items-start gap-3">
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-solar flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium">
                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">
                  {message.content.split('\n').map((line, i) => (
                    <span key={i}>
                      {line}
                      {i < message.content.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </p>
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-primary" />
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="ai-chat-bubble ai-chat-bubble-ai rounded-2xl p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-solar flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Analyzing simulation data...</span>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-solar-border">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask about your simulation..."
            className="flex-1 px-4 py-3 bg-solar-bg-card border border-solar-border rounded-xl focus:outline-none focus:border-primary transition-colors text-sm"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={cn(
              'p-3 rounded-xl transition-all',
              input.trim() && !isLoading
                ? 'bg-primary hover:bg-primary/90 text-white'
                : 'bg-solar-bg-card text-muted-foreground cursor-not-allowed'
            )}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          AI responses are based on simulation data. Always verify critical information.
        </p>
      </div>
    </div>
  )
}
