import { useState, useRef, useEffect } from 'react'
import { Send, MessageCircle, Loader2 } from 'lucide-react'
import { useStore } from '../../store/useStore'
import ReactMarkdown from 'react-markdown'

interface ChatPanelProps {
  onQuery: (query: string, selectedDate?: string) => void
}

export default function ChatPanel({ onQuery }: ChatPanelProps) {
  const { queryHistory, isQuerying } = useStore()
  const [input, setInput] = useState('')
  const [selectedDate, setSelectedDate] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [queryHistory])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isQuerying) return

    const trimmed = input.trim()
    // If user didn't type anything but selected a date, we'll still send a sensible default query.
    const effectiveQuery = trimmed || (selectedDate ? `Show ARGO data for ${selectedDate}` : 'Show ARGO data')

    if (!effectiveQuery && !selectedDate) return

    onQuery(effectiveQuery, selectedDate || undefined)
    setInput('')
  }

  return (
    <div className="flex flex-col h-full bg-ocean-medium">
      {/* Header */}
      <div className="p-4 border-b border-ocean-light">
        <h2 className="text-xl font-bold flex items-center space-x-2">
          <MessageCircle className="w-6 h-6 text-ocean-turquoise" />
          <span>Chat</span>
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {queryHistory.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>Start a conversation by asking a question about ocean data.</p>
          </div>
        )}
        {queryHistory.map((item, index) => (
          <div key={index} className="space-y-2">
            {/* User Query */}
            <div className="flex justify-end">
              <div className="bg-ocean-turquoise text-ocean-deep rounded-lg p-3 max-w-[80%]">
                <p className="text-sm">{item.query}</p>
              </div>
            </div>
            {/* AI Response */}
            <div className="flex justify-start">
              <div className="bg-ocean-light rounded-lg p-3 max-w-[80%]">
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{item.response.response}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isQuerying && (
          <div className="flex justify-start">
            <div className="bg-ocean-light rounded-lg p-3">
              <Loader2 className="w-5 h-5 animate-spin text-ocean-turquoise" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-ocean-light">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question... (optional)"
              className="flex-1 px-4 py-2 bg-ocean-deep text-white rounded-lg border border-ocean-turquoise focus:outline-none focus:ring-2 focus:ring-ocean-turquoise"
              disabled={isQuerying}
            />
            <button
              type="submit"
              disabled={(!input.trim() && !selectedDate) || isQuerying}
              className="px-4 py-2 bg-ocean-turquoise text-ocean-deep rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div>
            <label className="block text-xs text-gray-300 mb-2 font-semibold">📅 Select Date (ARGO Data)</label>
            <div className="flex space-x-2">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="flex-1 px-3 py-2 bg-ocean-deep text-white rounded-lg border border-ocean-light focus:outline-none focus:ring-2 focus:ring-ocean-turquoise text-sm"
                disabled={isQuerying}
              />
              {selectedDate && (
                <button
                  type="button"
                  onClick={() => setSelectedDate('')}
                  className="px-3 py-2 bg-ocean-light text-white rounded-lg hover:bg-ocean-medium transition-colors text-sm font-semibold"
                  disabled={isQuerying}
                >
                  Clear
                </button>
              )}
            </div>
            <p className="text-xs text-gray-400 mt-1">Leave date empty to show all floats, or select a date to filter data for that specific day.</p>
          </div>
        </form>
      </div>
    </div>
  )
}
