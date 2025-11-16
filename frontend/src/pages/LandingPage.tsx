import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Waves, Database, Brain, Map, BarChart, Settings, Linkedin, Phone, Code } from 'lucide-react'
import { useStore } from '../store/useStore'

// Simple UUID generator
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

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
      <header className="fixed top-0 left-0 right-0 bg-ocean-medium/90 backdrop-blur-md shadow-lg z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Waves className="w-8 h-8 text-ocean-turquoise" />
              <h1 className="text-2xl font-bold text-white">WavyAI</h1>
            </div>
            <nav className="hidden md:flex space-x-8 items-center">
              <a 
                href="#home" 
                onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                className="text-gray-300 hover:text-ocean-turquoise transition-colors"
              >
                Home
              </a>
              <a 
                href="#features" 
                onClick={(e) => { e.preventDefault(); document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }); }}
                className="text-gray-300 hover:text-ocean-turquoise transition-colors"
              >
                Features
              </a>
              <a 
                href="#about" 
                onClick={(e) => { e.preventDefault(); document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }); }}
                className="text-gray-300 hover:text-ocean-turquoise transition-colors"
              >
                About
              </a>
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

      {/* Home/Hero Section with Animated Background */}
      <section id="home" className="relative min-h-screen flex items-center justify-center pt-20">
        <div className="animated-ocean-background"></div>
        <div className="hero-bubbles"></div>
        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-ocean-turquoise to-white bg-clip-text text-transparent">
            AI-powered ocean insights, riding the waves of imagination.
          </h2>
          <p className="text-xl text-gray-300 mb-12">
            Turn deep ARGO data into smooth, effortless answers tailored to you.
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

          
          {/* Scroll Indicator */}
          <div className="mt-16 animate-bounce">
            <div className="flex flex-col items-center text-ocean-turquoise">
              <span className="text-sm mb-2">Scroll to explore</span>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-16">

        {/* Features Section */}
        <section id="features" className="max-w-6xl mx-auto mb-20 scroll-mt-20">
          <h3 className="text-3xl font-bold text-center mb-12 text-ocean-turquoise">Features</h3>
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

          {/* CTA Button to open chatbot/dashboard */}
          <div className="mt-12 flex justify-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-3 rounded-full bg-ocean-turquoise text-ocean-deep font-semibold text-lg shadow-lg hover:bg-opacity-90 hover:shadow-xl transition-all duration-200"
            >
              Begin Your Dive
            </button>
          </div>
        </section>

        {/* About Section with Team Cards */}
        <section id="about" className="max-w-6xl mx-auto mb-20 scroll-mt-20">
          <h3 className="text-3xl font-bold text-center mb-12 text-ocean-turquoise">Our Team</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Team Member 1 */}
            <div className="card text-center hover:scale-105 transition-transform duration-300">
              <div className="mb-4">
                <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-ocean-turquoise to-ocean-deep flex items-center justify-center text-4xl font-bold text-white">
                  G
                </div>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-ocean-turquoise">Gaurav Kumar</h4>
              <p className="text-gray-400 mb-4">Full Stack Developer</p>
              <div className="space-y-2">
                <a 
                  href="https://www.linkedin.com/in/gaurav-kumar-22592b30b/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center justify-center text-ocean-turquoise hover:text-white transition-colors"
                >
                  <Linkedin className="w-4 h-4 mr-2" />
                  <span className="text-sm">LinkedIn</span>
                </a>
                <a 
                  href="tel:+1234567890"
                  className="flex items-center justify-center text-gray-300 hover:text-ocean-turquoise transition-colors"
                >
                  <Phone className="w-4 h-4 mr-2" />
                  <span className="text-sm">8588069817</span>
                </a>
              </div>
            </div>

            {/* Team Member 2 */}
            <div className="card text-center hover:scale-105 transition-transform duration-300">
              <div className="mb-4">
                <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center text-4xl font-bold text-white">
                  KS
                </div>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-ocean-turquoise">Kushagra Srivastava</h4>
              <p className="text-gray-400 mb-4">Backend Developer</p>
              <div className="space-y-2">
                <a 
                  href="https://www.linkedin.com/in/kushagra-srivastava-a45b61213/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center justify-center text-ocean-turquoise hover:text-white transition-colors"
                >
                  <Linkedin className="w-4 h-4 mr-2" />
                  <span className="text-sm">LinkedIn</span>
                </a>
                <a 
                  href="tel:+1234567891"
                  className="flex items-center justify-center text-gray-300 hover:text-ocean-turquoise transition-colors"
                >
                  <Phone className="w-4 h-4 mr-2" />
                  <span className="text-sm">9198490950</span>
                </a>
              </div>
            </div>

            {/* Team Member 3 */}
            <div className="card text-center hover:scale-105 transition-transform duration-300">
              <div className="mb-4">
                <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-4xl font-bold text-white">
                  KV
                </div>
              </div>
              <h4 className="text-xl font-semibold mb-2 text-ocean-turquoise">Kushagra Verma</h4>
              <p className="text-gray-400 mb-4">Ai/Ml Engineer</p>
              <div className="space-y-2">
                <a 
                  href="https://www.linkedin.com/in/kushagra-verma-/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center justify-center text-ocean-turquoise hover:text-white transition-colors"
                >
                  <Linkedin className="w-4 h-4 mr-2" />
                  <span className="text-sm">LinkedIn</span>
                </a>
                <a 
                  href="tel:+1234567892"
                  className="flex items-center justify-center text-gray-300 hover:text-ocean-turquoise transition-colors"
                >
                  <Phone className="w-4 h-4 mr-2" />
                  <span className="text-sm">9236930458</span>
                </a>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
