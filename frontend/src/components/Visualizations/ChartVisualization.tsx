import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { QueryResponse, visualizationAPI } from '../../services/api'
import { Download } from 'lucide-react'

interface ChartVisualizationProps {
  query: QueryResponse | null
}

export default function ChartVisualization({ query }: ChartVisualizationProps) {
  const [chartData, setChartData] = useState<any[]>([])

  useEffect(() => {
    // Generate sample data based on query
    if (query?.visualization) {
      const config = query.visualization.config
      const data = []
      
      // Generate sample data for demonstration
      for (let i = 0; i < 50; i++) {
        const depth = i * 40
        data.push({
          depth,
          temperature: 25 - depth / 100 + Math.random() * 2 - 1,
          salinity: 35 + Math.random() * 0.5 - 0.25,
          pressure: depth / 10,
        })
      }
      
      setChartData(data)
    }
  }, [query])

  if (!query?.visualization) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">No visualization data available</p>
      </div>
    )
  }

  const config = query.visualization.config

  return (
    <div className="p-4 h-full bg-ocean-deep">
      <h3 className="text-lg font-semibold mb-4">{query.visualization.title}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1B3A57" />
          <XAxis 
            dataKey={config.x_axis || 'depth'} 
            stroke="#1EE3CF"
            label={{ value: config.x_axis || 'Depth (m)', position: 'insideBottom', offset: -5, fill: '#1EE3CF' }}
          />
          <YAxis 
            stroke="#1EE3CF"
            label={{ value: config.y_axis || 'Temperature (°C)', angle: -90, position: 'insideLeft', fill: '#1EE3CF' }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1B3A57', border: '1px solid #1EE3CF', borderRadius: '8px' }}
            labelStyle={{ color: '#1EE3CF' }}
          />
          <Legend />
          {config.y_axis === 'temperature' && (
            <Line 
              type="monotone" 
              dataKey="temperature" 
              stroke="#1EE3CF" 
              strokeWidth={2}
              dot={false}
              name="Temperature (°C)"
            />
          )}
          {config.y_axis === 'salinity' && (
            <Line 
              type="monotone" 
              dataKey="salinity" 
              stroke="#FF6B6B" 
              strokeWidth={2}
              dot={false}
              name="Salinity (PSU)"
            />
          )}
          {config.y_axis === 'pressure' && (
            <Line 
              type="monotone" 
              dataKey="pressure" 
              stroke="#1EE3CF" 
              strokeWidth={2}
              dot={false}
              name="Pressure (dbar)"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

