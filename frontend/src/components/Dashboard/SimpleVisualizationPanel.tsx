import { useEffect, useState } from 'react'
import { Map, BarChart3, Download } from 'lucide-react'
import { useStore } from '../../store/useStore'
import SimpleLeafletMap from '../Visualizations/SimpleLeafletMap'
import SimpleChart from '../Visualizations/SimpleChart'
import { visualizationAPI } from '../../services/api'

export default function SimpleVisualizationPanel() {
  const { currentQuery } = useStore()
  const [visualizationType, setVisualizationType] = useState<'map' | 'chart'>('map')
  const [chartType, setChartType] = useState<'temperature-depth' | 'salinity-depth' | 'temperature-trend'>('temperature-depth')
  const [selectedProfileId, setSelectedProfileId] = useState<string>('profile_5906468_001')

  useEffect(() => {
    if (currentQuery?.visualization) {
      const vizType = currentQuery.visualization.type
      if (vizType === 'map') {
        setVisualizationType('map')
      } else if (vizType === 'line_chart') {
        setVisualizationType('chart')
        // Determine chart type based on config
        const config = currentQuery.visualization.config
        if (config?.x_axis === 'temperature') {
          setChartType('temperature-depth')
        } else if (config?.x_axis === 'salinity') {
          setChartType('salinity-depth')
        } else if (config?.x_axis === 'time') {
          setChartType('temperature-trend')
        }
      } else if (vizType === 'time_series') {
        setVisualizationType('chart')
        setChartType('temperature-trend')
      }
    }
  }, [currentQuery])

  const handleDownload = async () => {
    try {
      if (visualizationType === 'chart' && (chartType === 'temperature-depth' || chartType === 'salinity-depth')) {
        const blob = await visualizationAPI.exportProfileCSV(selectedProfileId)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `argo_profile_${selectedProfileId}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } else {
        // For map or other visualizations, create a simple data export
        const data = "# WavyAI Data Export\n# Generated on: " + new Date().toISOString() + "\n# Response: " + (currentQuery?.response || 'N/A')
        const blob = new Blob([data], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'wavyai_export.txt'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="flex flex-col h-full bg-ocean-deep">
      {/* Header */}
      <div className="p-4 border-b border-ocean-medium flex justify-between items-center">
        <h2 className="text-xl font-bold flex items-center space-x-2">
          {visualizationType === 'map' ? (
            <Map className="w-6 h-6 text-ocean-turquoise" />
          ) : (
            <BarChart3 className="w-6 h-6 text-ocean-turquoise" />
          )}
          <span>Visualization</span>
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setVisualizationType('map')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              visualizationType === 'map'
                ? 'bg-ocean-turquoise text-ocean-deep'
                : 'bg-ocean-medium text-white hover:bg-ocean-light'
            }`}
          >
            Map
          </button>
          <button
            onClick={() => setVisualizationType('chart')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              visualizationType === 'chart'
                ? 'bg-ocean-turquoise text-ocean-deep'
                : 'bg-ocean-medium text-white hover:bg-ocean-light'
            }`}
          >
            Chart
          </button>
          <button 
            onClick={handleDownload}
            className="px-4 py-2 bg-ocean-medium text-white rounded-lg hover:bg-ocean-light transition-colors"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Chart Type Selector (when chart is selected) */}
      {visualizationType === 'chart' && (
        <div className="p-3 border-b border-ocean-medium bg-ocean-medium">
          <div className="flex space-x-2">
            <button
              onClick={() => setChartType('temperature-depth')}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                chartType === 'temperature-depth'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-light text-white hover:bg-ocean-turquoise hover:text-ocean-deep'
              }`}
            >
              Temperature
            </button>
            <button
              onClick={() => setChartType('salinity-depth')}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                chartType === 'salinity-depth'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-light text-white hover:bg-ocean-turquoise hover:text-ocean-deep'
              }`}
            >
              Salinity
            </button>
            <button
              onClick={() => setChartType('temperature-trend')}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                chartType === 'temperature-trend'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-light text-white hover:bg-ocean-turquoise hover:text-ocean-deep'
              }`}
            >
              Trends
            </button>
          </div>
        </div>
      )}

      {/* Visualization Content */}
      <div className="flex-1 overflow-hidden p-4">
        {visualizationType === 'map' ? (
          <SimpleLeafletMap height="100%" />
        ) : (
          <SimpleChart 
            type={chartType}
            profileId={selectedProfileId}
            height={400}
          />
        )}
      </div>

      {/* Info Panel */}
      <div className="p-3 border-t border-ocean-medium bg-ocean-medium text-sm text-gray-300">
        {visualizationType === 'map' ? (
          <p>🌊 Showing ARGO float locations worldwide. Click markers for details.</p>
        ) : (
          <p>📊 Ocean profile data from ARGO floats. Use download button to export data.</p>
        )}
      </div>
    </div>
  )
}
