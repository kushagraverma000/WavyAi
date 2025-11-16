import { useState, useEffect } from 'react'
import { Download, Database, RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface DataSummary {
  total_floats: number
  total_profiles: number
  total_files: number
  data_size_mb: number
  date_range: string
  last_updated: string
}

interface DataStatus {
  status: string
  floats_loaded: number
  profiles_loaded: number
  ready_for_queries: boolean
  message: string
}

export default function DataSetupPanel() {
  const [dataSummary, setDataSummary] = useState<DataSummary | null>(null)
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [fetchingData, setFetchingData] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadDataSummary()
    loadDataStatus()
    
    // Poll status every 30 seconds
    const interval = setInterval(() => {
      loadDataStatus()
      if (!fetchingData) {
        loadDataSummary()
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchingData])

  const loadDataSummary = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/data-management/data-summary`)
      if (response.ok) {
        const data = await response.json()
        setDataSummary(data)
      }
    } catch (error) {
      console.error('Failed to load data summary:', error)
    }
  }

  const loadDataStatus = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/data-management/data-status`)
      if (response.ok) {
        const data = await response.json()
        setDataStatus(data)
      }
    } catch (error) {
      console.error('Failed to load data status:', error)
    }
  }

  const fetchArgoData = async () => {
    setFetchingData(true)
    setLoading(true)
    setMessage('Starting ARGO data fetch from official sources...')

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/data-management/fetch-argo-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          days_back: 30,
          max_files: 50,
          force_refresh: false
        })
      })

      if (response.ok) {
        const result = await response.json()
        setMessage(`${result.message}. This will take ${result.estimated_time}.`)
        
        // Poll for completion
        setTimeout(() => {
          setFetchingData(false)
          setMessage('Data fetch completed! Refresh to see updated statistics.')
        }, 300000) // 5 minutes
        
      } else {
        throw new Error('Failed to start data fetch')
      }
    } catch (error) {
      console.error('Failed to fetch ARGO data:', error)
      setMessage('Failed to fetch ARGO data. Please try again.')
      setFetchingData(false)
    } finally {
      setLoading(false)
    }
  }

  const initializeSampleData = async () => {
    setLoading(true)
    setMessage('Initializing sample ARGO data for immediate testing...')

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/data-management/initialize-sample-data`, {
        method: 'POST'
      })

      if (response.ok) {
        const result = await response.json()
        setMessage(`${result.message}. This will take ${result.estimated_time}.`)
        
        // Refresh data after a delay
        setTimeout(() => {
          loadDataSummary()
          loadDataStatus()
          setMessage('Sample data initialized successfully!')
        }, 120000) // 2 minutes
        
      } else {
        throw new Error('Failed to initialize sample data')
      }
    } catch (error) {
      console.error('Failed to initialize sample data:', error)
      setMessage('Failed to initialize sample data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = () => {
    if (!dataStatus) return <Clock className="w-5 h-5 text-gray-400" />
    
    switch (dataStatus.status) {
      case 'ready':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'no_data':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
      default:
        return <Clock className="w-5 h-5 text-blue-500" />
    }
  }

  const getStatusColor = () => {
    if (!dataStatus) return 'text-gray-400'
    
    switch (dataStatus.status) {
      case 'ready':
        return 'text-green-500'
      case 'no_data':
        return 'text-yellow-500'
      default:
        return 'text-blue-500'
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-ocean-deep rounded-lg">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">ARGO Data Setup</h1>
        <p className="text-gray-300">
          Set up real oceanographic data from official ARGO sources to power your AI assistant
        </p>
      </div>

      {/* Status Card */}
      <div className="bg-ocean-medium rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
            {getStatusIcon()}
            <span>Data Status</span>
          </h2>
          <button
            onClick={() => {
              loadDataSummary()
              loadDataStatus()
            }}
            className="p-2 bg-ocean-light rounded-lg hover:bg-ocean-turquoise transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {dataStatus && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-ocean-turquoise">{dataStatus.floats_loaded}</div>
              <div className="text-sm text-gray-400">ARGO Floats</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-ocean-turquoise">{dataStatus.profiles_loaded}</div>
              <div className="text-sm text-gray-400">Profiles</div>
            </div>
            <div className="text-center">
              <div className={`text-sm font-medium ${getStatusColor()}`}>
                {dataStatus.ready_for_queries ? 'Ready for Queries' : 'Setup Required'}
              </div>
              <div className="text-xs text-gray-400 mt-1">{dataStatus.message}</div>
            </div>
          </div>
        )}

        {dataSummary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Files:</span>
              <span className="ml-2 text-white">{dataSummary.total_files}</span>
            </div>
            <div>
              <span className="text-gray-400">Size:</span>
              <span className="ml-2 text-white">{dataSummary.data_size_mb.toFixed(1)} MB</span>
            </div>
            <div>
              <span className="text-gray-400">Date Range:</span>
              <span className="ml-2 text-white">{dataSummary.date_range}</span>
            </div>
            <div>
              <span className="text-gray-400">Updated:</span>
              <span className="ml-2 text-white">{dataSummary.last_updated}</span>
            </div>
          </div>
        )}
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Real Data Card */}
        <div className="bg-ocean-medium rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Download className="w-8 h-8 text-ocean-turquoise" />
            <div>
              <h3 className="text-lg font-semibold text-white">Real ARGO Data</h3>
              <p className="text-sm text-gray-400">From official sources</p>
            </div>
          </div>
          
          <p className="text-gray-300 mb-4">
            Download recent oceanographic data from official ARGO data centers including 
            temperature, salinity, and biogeochemical measurements.
          </p>
          
          <ul className="text-sm text-gray-400 mb-6 space-y-1">
            <li>• Last 30 days of data</li>
            <li>• Up to 50 recent profiles</li>
            <li>• Global ocean coverage</li>
            <li>• Quality-controlled measurements</li>
          </ul>
          
          <button
            onClick={fetchArgoData}
            disabled={loading || fetchingData}
            className="w-full bg-ocean-turquoise text-ocean-deep font-semibold py-3 px-4 rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Fetching...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Fetch Real Data</span>
              </>
            )}
          </button>
        </div>

        {/* Sample Data Card */}
        <div className="bg-ocean-medium rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="w-8 h-8 text-blue-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">Sample Data</h3>
              <p className="text-sm text-gray-400">For immediate testing</p>
            </div>
          </div>
          
          <p className="text-gray-300 mb-4">
            Generate realistic sample ARGO data for immediate testing and development. 
            Perfect for getting started quickly.
          </p>
          
          <ul className="text-sm text-gray-400 mb-6 space-y-1">
            <li>• 50+ sample floats</li>
            <li>• Realistic profiles</li>
            <li>• Global distribution</li>
            <li>• Ready in minutes</li>
          </ul>
          
          <button
            onClick={initializeSampleData}
            disabled={loading}
            className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Initializing...</span>
              </>
            ) : (
              <>
                <Database className="w-4 h-4" />
                <span>Initialize Sample Data</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className="bg-ocean-light rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <Clock className="w-5 h-5 text-ocean-turquoise mt-0.5" />
            <div>
              <p className="text-white">{message}</p>
              {fetchingData && (
                <p className="text-sm text-gray-400 mt-2">
                  The system is downloading and processing data in the background. 
                  You can continue using the application while this completes.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-ocean-light rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-3">Next Steps</h3>
        <ol className="text-gray-300 space-y-2">
          <li>1. <strong>Choose your data source:</strong> Real ARGO data for production or sample data for testing</li>
          <li>2. <strong>Wait for processing:</strong> Data will be downloaded and loaded into the database</li>
          <li>3. <strong>Start querying:</strong> Once ready, ask questions about ocean data in the chat</li>
          <li>4. <strong>Explore visualizations:</strong> View maps, charts, and data tables</li>
          <li>5. <strong>Export data:</strong> Download results in CSV or NetCDF formats</li>
        </ol>
      </div>
    </div>
  )
}
