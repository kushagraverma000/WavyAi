import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { QueryResponse, visualizationAPI } from '../../services/api'
import { Download, BarChart3, TrendingUp } from 'lucide-react'

interface ChartVisualizationProps {
  query: QueryResponse | null
}

export default function EnhancedChartVisualization({ query }: ChartVisualizationProps) {
  const [chartData, setChartData] = useState<any[]>([])
  const [chartType, setChartType] = useState<'temperature' | 'salinity' | 'ts-diagram'>('temperature')
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null)
  const [profiles, setProfiles] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  // Use data from query response if available
  useEffect(() => {
    if (query?.visualization?.data) {
      const vizData = query.visualization.data
      const vizType = query.visualization.type
      
      // Set chart data directly from query
      if (Array.isArray(vizData)) {
        setChartData(vizData)
        
        // Determine chart type from visualization config
        const config = query.visualization.config || {}
        if (vizType === 'temperature_depth_chart' || config.x_axis === 'temperature') {
          setChartType('temperature')
        } else if (vizType === 'salinity_depth_chart' || config.x_axis === 'salinity') {
          setChartType('salinity')
        } else if (vizType === 'time_series') {
          // For time series, we'll show as line chart
          setChartType('temperature')
        }
      }
    } else {
      // Fallback to loading from API
      loadProfiles()
    }
  }, [query])

  // Load available profiles
  const loadProfiles = async () => {
    try {
      const response = await visualizationAPI.searchProfiles({ limit: 20 })
      setProfiles(response.profiles || [])
      if (response.profiles && response.profiles.length > 0) {
        setSelectedProfile(response.profiles[0].profile_id)
      }
    } catch (error) {
      console.error('Failed to load profiles:', error)
    }
  }

  // Load chart data when profile or type changes (only if not using query data)
  useEffect(() => {
    if (selectedProfile && (!query?.visualization?.data)) {
      loadChartData(selectedProfile, chartType)
    }
  }, [selectedProfile, chartType, query])

  const loadChartData = async (profileId: string, type: string) => {
    setLoading(true)
    try {
      let response
      switch (type) {
        case 'temperature':
          response = await visualizationAPI.getTemperatureDepthChart(profileId)
          break
        case 'salinity':
          response = await visualizationAPI.getSalinityDepthChart(profileId)
          break
        case 'ts-diagram':
          response = await visualizationAPI.getTSDiagram(profileId)
          break
        default:
          response = await visualizationAPI.getTemperatureDepthChart(profileId)
      }
      setChartData(response.data || [])
    } catch (error) {
      console.error('Failed to load chart data:', error)
      setChartData([])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    if (!selectedProfile) return
    
    try {
      const blob = await visualizationAPI.exportProfileCSV(selectedProfile)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `argo_profile_${selectedProfile}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to export data:', error)
    }
  }

  const renderChart = () => {
    if (loading && !query?.visualization?.data) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-ocean-turquoise">Loading chart data...</div>
        </div>
      )
    }

    if (!chartData || chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-400">No chart data available</div>
        </div>
      )
    }

    // Check if this is a time series (has 'date' field)
    const isTimeSeries = chartData.length > 0 && chartData[0].date

    if (chartType === 'ts-diagram' && chartData[0].salinity && chartData[0].temperature) {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B3A57" />
            <XAxis 
              dataKey="salinity" 
              stroke="#1EE3CF"
              label={{ value: 'Salinity (PSU)', position: 'insideBottom', offset: -5, fill: '#1EE3CF' }}
            />
            <YAxis 
              dataKey="temperature"
              stroke="#1EE3CF"
              label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft', fill: '#1EE3CF' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1B3A57', border: '1px solid #1EE3CF', borderRadius: '8px' }}
              labelStyle={{ color: '#1EE3CF' }}
            />
            <Scatter 
              dataKey="temperature" 
              fill="#1EE3CF"
              name="T-S Points"
            />
          </ScatterChart>
        </ResponsiveContainer>
      )
    }

    // Time series chart
    if (isTimeSeries) {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B3A57" />
            <XAxis 
              dataKey="date" 
              stroke="#1EE3CF"
              label={{ value: 'Date', position: 'insideBottom', offset: -5, fill: '#1EE3CF' }}
            />
            <YAxis 
              dataKey="temperature"
              stroke="#1EE3CF"
              label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft', fill: '#1EE3CF' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1B3A57', border: '1px solid #1EE3CF', borderRadius: '8px' }}
              labelStyle={{ color: '#1EE3CF' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="temperature" 
              stroke="#1EE3CF" 
              strokeWidth={2}
              dot={false}
              name="Temperature (°C)"
            />
          </LineChart>
        </ResponsiveContainer>
      )
    }

    // Depth profile chart (depth vs temperature/salinity)
    return (
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1B3A57" />
          <XAxis 
            dataKey={chartType === 'temperature' ? 'temperature' : 'salinity'} 
            stroke="#1EE3CF"
            label={{ 
              value: chartType === 'temperature' ? 'Temperature (°C)' : 'Salinity (PSU)', 
              position: 'insideBottom', 
              offset: -5, 
              fill: '#1EE3CF' 
            }}
          />
          <YAxis 
            dataKey="depth"
            stroke="#1EE3CF"
            reversed={true}
            label={{ value: 'Depth (m)', angle: -90, position: 'insideLeft', fill: '#1EE3CF' }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1B3A57', border: '1px solid #1EE3CF', borderRadius: '8px' }}
            labelStyle={{ color: '#1EE3CF' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey={chartType} 
            stroke="#1EE3CF" 
            strokeWidth={2}
            dot={false}
            name={chartType === 'temperature' ? 'Temperature (°C)' : 'Salinity (PSU)'}
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  return (
    <div className="flex flex-col h-full bg-ocean-deep">
      {/* Controls */}
      <div className="p-4 border-b border-ocean-medium">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Profile Selection */}
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-300">Profile:</label>
            <select
              value={selectedProfile || ''}
              onChange={(e) => setSelectedProfile(e.target.value)}
              className="bg-ocean-medium text-white border border-ocean-turquoise rounded px-2 py-1 text-sm"
            >
              {profiles.map((profile) => (
                <option key={profile.profile_id} value={profile.profile_id}>
                  Float {profile.float_id} - Profile {profile.profile_number}
                </option>
              ))}
            </select>
          </div>

          {/* Chart Type Selection */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setChartType('temperature')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                chartType === 'temperature'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-medium text-white hover:bg-ocean-light'
              }`}
            >
              <TrendingUp className="w-4 h-4 inline mr-1" />
              Temperature
            </button>
            <button
              onClick={() => setChartType('salinity')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                chartType === 'salinity'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-medium text-white hover:bg-ocean-light'
              }`}
            >
              <BarChart3 className="w-4 h-4 inline mr-1" />
              Salinity
            </button>
            <button
              onClick={() => setChartType('ts-diagram')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                chartType === 'ts-diagram'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-medium text-white hover:bg-ocean-light'
              }`}
            >
              T-S Diagram
            </button>
          </div>

          {/* Export Button */}
          <button
            onClick={handleExport}
            disabled={!selectedProfile}
            className="px-3 py-1 bg-ocean-medium text-white rounded hover:bg-ocean-light transition-colors disabled:opacity-50 text-sm"
          >
            <Download className="w-4 h-4 inline mr-1" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 p-4">
        {renderChart()}
      </div>
    </div>
  )
}
