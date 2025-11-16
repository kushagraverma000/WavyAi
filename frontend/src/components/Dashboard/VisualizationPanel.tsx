import { useEffect, useState } from 'react'
import { Map, BarChart3, Download } from 'lucide-react'
import { useStore } from '../../store/useStore'
import SimpleMapVisualization from '../Visualizations/SimpleMapVisualization'
import EnhancedChartVisualization from '../Visualizations/EnhancedChartVisualization'

export default function VisualizationPanel() {
  const { currentQuery } = useStore()
  const [visualizationType, setVisualizationType] = useState<'map' | 'chart'>('map')

  useEffect(() => {
    if (currentQuery?.visualization) {
      const vizType = currentQuery.visualization.type
      if (vizType === 'map' || vizType === 'ts_diagram' || vizType === 'line_chart') {
        setVisualizationType(vizType === 'map' ? 'map' : 'chart')
      }
    }
  }, [currentQuery])

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
          <button className="px-4 py-2 bg-ocean-medium text-white rounded-lg hover:bg-ocean-light transition-colors">
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Visualization Content */}
      <div className="flex-1 overflow-hidden">
        {visualizationType === 'map' ? (
          <SimpleMapVisualization query={currentQuery} />
        ) : (
          <EnhancedChartVisualization query={currentQuery} />
        )}
      </div>
    </div>
  )
}

