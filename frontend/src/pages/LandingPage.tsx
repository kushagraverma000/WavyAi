import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Waves, Database, Brain, Map, BarChart, Settings } from 'lucide-react'
import { useStore } from '../store/useStore'

// Simple UUID generator
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const exampleQueries = [
  "Show me temperature profiles in the Atlantic Ocean",
  "What is the salinity at 1000 meters depth?",
  "Find oxygen levels for fisheries management",
  "Display ARGO float locations on a map",
  "Explain ocean temperature trends",
  "Compare temperature and salinity profiles",
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { setSessionId } = useStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [sessionId] = useState(() => generateUUID())

  useEffect(() => {
    setSessionId(sessionId)
  }, [sessionId, setSessionId])

  const handleSearch = (query?: string) => {
    const q = query || searchQuery
    if (q.trim()) {
      navigate(`/dashboard?q=${encodeURIComponent(q)}`)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background */}
      <div className="wave-background"></div>

      {/* Header */}
      <header className="bg-ocean-medium shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <Waves className="w-8 h-8 text-ocean-turquoise" />
              <h1 className="text-2xl font-bold text-white">WavyAI</h1>
            </div>
            <nav className="hidden md:flex space-x-8 items-center">
              <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#about" className="text-gray-300 hover:text-white transition-colors">About</a>
              <button
                onClick={() => navigate('/setup')}
                className="flex items-center space-x-2 bg-ocean-turquoise text-ocean-deep px-4 py-2 rounded-lg hover:bg-opacity-90 transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span>Data Setup</span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto text-center mb-20">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-ocean-turquoise to-white bg-clip-text text-transparent">
            AI-Powered Ocean Data Exploration
          </h2>
          <p className="text-xl text-gray-300 mb-12">
            Ask questions about ARGO float data in natural language. Get intelligent, adaptive
            responses tailored to your expertise level.
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ask me anything about ocean data..."
              className="w-full px-6 py-4 pr-14 bg-ocean-medium text-white rounded-full border-2 border-ocean-turquoise focus:outline-none focus:ring-2 focus:ring-ocean-turquoise text-lg"
            />
            <button
              onClick={() => handleSearch()}
              className="absolute right-2 top-2 p-2 bg-ocean-turquoise text-ocean-deep rounded-full hover:bg-opacity-90 transition-colors"
            >
              <Search className="w-6 h-6" />
            </button>
          </div>

          {/* Example Queries */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-12">
            {exampleQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => handleSearch(query)}
                className="p-4 bg-ocean-medium hover:bg-ocean-light rounded-lg text-left transition-colors border border-ocean-turquoise border-opacity-30 hover:border-opacity-100"
              >
                <p className="text-sm text-gray-300">{query}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <section id="features" className="max-w-6xl mx-auto mb-20">
          <h3 className="text-3xl font-bold text-center mb-12">Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card text-center">
              <Brain className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">AI-Powered</h4>
              <p className="text-gray-300">
                Natural language queries with intelligent, adaptive responses
              </p>
            </div>
            <div className="card text-center">
              <Map className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">Interactive Maps</h4>
              <p className="text-gray-300">
                Visualize ARGO float locations and ocean data on interactive maps
              </p>
            </div>
            <div className="card text-center">
              <BarChart className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">Dynamic Visualizations</h4>
              <p className="text-gray-300">
                Generate charts and plots based on your queries and user type
              </p>
            </div>
            <div className="card text-center">
              <Database className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">Real-Time Data</h4>
              <p className="text-gray-300">
                Access the latest ARGO float data with incremental updates
              </p>
            </div>
            <div className="card text-center">
              <Waves className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">Multi-Audience</h4>
              <p className="text-gray-300">
                Tailored experiences for researchers, students, managers, and more
              </p>
            </div>
            <div className="card text-center">
              <Search className="w-12 h-12 text-ocean-turquoise mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-2">Hybrid Search</h4>
              <p className="text-gray-300">
                Combines vector similarity search with SQL filtering
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

