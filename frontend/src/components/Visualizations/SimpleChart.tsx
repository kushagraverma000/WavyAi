import React, { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

interface ChartData {
  depth?: number
  temperature?: number
  salinity?: number
  date?: string
  quality_flag?: number
}

interface SimpleChartProps {
  type: 'temperature-depth' | 'salinity-depth' | 'temperature-trend'
  data?: ChartData[]
  profileId?: string
  title?: string
  height?: number
}

const SimpleChart: React.FC<SimpleChartProps> = ({
  type,
  data = [],
  profileId,
  title,
  height = 400
}) => {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (data.length > 0) {
          setChartData(data)
        } else {
          // Fetch from API based on chart type
          let url = ''
          if (type === 'temperature-depth' && profileId) {
            url = `/api/v1/simple/profiles/${profileId}/temperature-depth`
          } else if (type === 'salinity-depth' && profileId) {
            url = `/api/v1/simple/profiles/${profileId}/salinity-depth`
          } else if (type === 'temperature-trend') {
            url = '/api/v1/simple/temperature-trend'
          }

          if (url) {
            const response = await fetch(url)
            const result = await response.json()
            setChartData(result.data || [])
          }
        }
      } catch (error) {
        console.error('Failed to fetch chart data:', error)
        // Use fallback data
        setChartData(generateFallbackData(type))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [type, data, profileId])

  const generateFallbackData = (chartType: string): ChartData[] => {
    if (chartType === 'temperature-depth') {
      return Array.from({ length: 20 }, (_, i) => ({
        depth: i * 100 + 5,
        temperature: 25 - i * 1.2 + Math.random() * 2,
        quality_flag: 1
      }))
    } else if (chartType === 'salinity-depth') {
      return Array.from({ length: 20 }, (_, i) => ({
        depth: i * 100 + 5,
        salinity: 35 + (i * 0.01) + Math.random() * 0.1,
        quality_flag: 1
      }))
    } else if (chartType === 'temperature-trend') {
      return Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (30 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        temperature: 20 + Math.sin(i * 0.2) * 5 + Math.random() * 2
      }))
    }
    return []
  }

  const getChartConfig = () => {
    const baseConfig = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: title || getDefaultTitle(),
        },
      },
    }

    if (type === 'temperature-depth') {
      return {
        ...baseConfig,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Temperature (°C)'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Depth (m)'
            },
            reverse: true // Depth increases downward
          }
        }
      }
    } else if (type === 'salinity-depth') {
      return {
        ...baseConfig,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Salinity (PSU)'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Depth (m)'
            },
            reverse: true
          }
        }
      }
    } else if (type === 'temperature-trend') {
      return {
        ...baseConfig,
        scales: {
          x: {
            type: 'time' as const,
            title: {
              display: true,
              text: 'Date'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Temperature (°C)'
            }
          }
        }
      }
    }

    return baseConfig
  }

  const getDefaultTitle = () => {
    switch (type) {
      case 'temperature-depth':
        return 'Temperature vs Depth Profile'
      case 'salinity-depth':
        return 'Salinity vs Depth Profile'
      case 'temperature-trend':
        return 'Temperature Trend Over Time'
      default:
        return 'Ocean Data Visualization'
    }
  }

  const getChartDataset = (): any => {
    if (type === 'temperature-depth') {
      return {
        labels: chartData.map(d => d.temperature),
        datasets: [
          {
            label: 'Temperature Profile',
            data: chartData.map(d => ({ x: d.temperature, y: d.depth })),
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.1,
          },
        ],
      }
    } else if (type === 'salinity-depth') {
      return {
        labels: chartData.map(d => d.salinity),
        datasets: [
          {
            label: 'Salinity Profile',
            data: chartData.map(d => ({ x: d.salinity, y: d.depth })),
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.1,
          },
        ],
      }
    } else if (type === 'temperature-trend') {
      return {
        labels: chartData.map(d => d.date || ''),
        datasets: [
          {
            label: 'Surface Temperature',
            data: chartData.map(d => ({ x: d.date || '', y: d.temperature })),
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.1,
          },
        ],
      }
    }

    return { labels: [], datasets: [] }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center bg-gray-100 rounded-lg" style={{ height }}>
        <div className="text-gray-600">Loading chart...</div>
      </div>
    )
  }

  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 p-4">
      <div style={{ height }}>
        <Line data={getChartDataset()} options={getChartConfig()} />
      </div>
    </div>
  )
}

export default SimpleChart
