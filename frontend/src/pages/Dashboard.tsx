import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import ChatPanel from '../components/Dashboard/ChatPanel'
import VisualizationPanel from '../components/Dashboard/VisualizationPanel'
import ContextPanel from '../components/Dashboard/ContextPanel'
import DataTablePanel from '../components/Dashboard/DataTablePanel'
import { useStore } from '../store/useStore'
import { queryAPI } from '../services/api'

// Simple UUID generator
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export default function Dashboard() {
  const [searchParams] = useSearchParams()
  const { sessionId, setSessionId, setUserType, addQuery, setIsQuerying, currentQuery } = useStore()
  const [initialQuery, setInitialQuery] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'visualization' | 'data'>('visualization')

  // Initialize session if not exists
  useEffect(() => {
    if (!sessionId) {
      setSessionId(generateUUID())
    }
  }, [sessionId, setSessionId])

  useEffect(() => {
    const q = searchParams.get('q')
    if (q) {
      setInitialQuery(q)
    }
  }, [searchParams])

  useEffect(() => {
    if (initialQuery && sessionId) {
      handleQuery(initialQuery)
      setInitialQuery(null)
    }
  }, [initialQuery, sessionId])

  const handleQuery = async (query: string, selectedDate?: string) => {
    if (!query.trim() && !selectedDate) return

    setIsQuerying(true)
    try {
      // If only date is selected, create a default query
      const finalQuery = query.trim() || (selectedDate ? `Show ARGO data for ${selectedDate}` : '')
      const response = await queryAPI.query({
        query: finalQuery,
        session_id: sessionId || undefined,
        selected_date: selectedDate,
      })
      addQuery(finalQuery, response)
      if (response.user_type) {
        setUserType(response.user_type)
      }
    } catch (error) {
      console.error('Query failed:', error)
    } finally {
      setIsQuerying(false)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-ocean-deep">
      {/* Three-Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className="w-1/4 border-r border-ocean-medium flex flex-col">
          <ChatPanel onQuery={handleQuery} />
        </div>

        {/* Main Content Panel with Tabs */}
        <div className="flex-1 flex flex-col">
          {/* Tab Navigation */}
          <div className="flex border-b border-ocean-medium bg-ocean-medium">
            <button
              onClick={() => setActiveTab('visualization')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'visualization'
                  ? 'bg-ocean-deep text-ocean-turquoise border-b-2 border-ocean-turquoise'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Visualizations
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'data'
                  ? 'bg-ocean-deep text-ocean-turquoise border-b-2 border-ocean-turquoise'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Data Tables
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'visualization' ? (
              <VisualizationPanel />
            ) : (
              <DataTablePanel query={currentQuery} />
            )}
          </div>
        </div>

        {/* Context Panel */}
        <div className="w-1/4 border-l border-ocean-medium flex flex-col">
          <ContextPanel />
        </div>
      </div>
    </div>
  )
}

