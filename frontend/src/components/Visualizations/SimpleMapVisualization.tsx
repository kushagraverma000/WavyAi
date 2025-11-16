import { useEffect, useState } from 'react'
import { QueryResponse, visualizationAPI } from '../../services/api'
import { MapPin, Navigation } from 'lucide-react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface SimpleMapVisualizationProps {
  query: QueryResponse | null
}

// Custom icon for ARGO floats
const argoIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="8" fill="#1EE3CF" stroke="#0284c7" stroke-width="2"/>
      <circle cx="12" cy="12" r="3" fill="white"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12]
})

export default function SimpleMapVisualization({ query }: SimpleMapVisualizationProps) {
  const [floats, setFloats] = useState<any[]>([
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [-30.1, 45.2] },
      properties: { id: '5906468', name: 'North Atlantic Float', status: 'active', last_update: '2024-11-10', total_profiles: 156 }
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [-140.2, 0.5] },
      properties: { id: '5906469', name: 'Pacific Equatorial Float', status: 'active', last_update: '2024-11-12', total_profiles: 142 }
    },
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [85.4, -55.3] },
      properties: { id: '5906470', name: 'Southern Ocean Float', status: 'active', last_update: '2024-11-08', total_profiles: 168 }
    }
  ])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Use data from query response if available
    if (query?.visualization?.data?.features && query.visualization.data.features.length > 0) {
      setFloats(query.visualization.data.features)
      setLoading(false)
    } else {
      const meta = (query?.metadata || {}) as any
      const selectedDay = typeof meta.selected_date === 'string' ? meta.selected_date : undefined
      loadFloats(selectedDay)
    }
  }, [query])

  const loadFloats = async (day?: string) => {
    setLoading(true)
    try {
      const data = await visualizationAPI.getFloatLocations({ limit: 20, day })
      if (data.features && data.features.length > 0) {
        setFloats(data.features)
      }
    } catch (error) {
      console.error('Failed to load floats:', error)
      // Keep default floats already set in state
    } finally {
      setLoading(false)
    }
  }

  // Always show the map even while loading (with initial data)
  // Only show loading state if there's no data at all
  if (loading && floats.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-ocean-turquoise">Loading map data...</div>
      </div>
    )
  }

  // Calculate center from floats or use default
  let center: [number, number] = [20, 0]
  if (floats.length > 0) {
    const coords = floats.map(f => f.geometry?.coordinates || [0, 0])
    const avgLon = coords.reduce((sum, c) => sum + c[0], 0) / coords.length
    const avgLat = coords.reduce((sum, c) => sum + c[1], 0) / coords.length
    center = [avgLat, avgLon]
  }

  return (
    <div className="h-full bg-ocean-deep flex flex-col">
      <div className="p-4 border-b border-ocean-medium">
        <div className="flex items-center">
          <Navigation className="w-5 h-5 text-ocean-turquoise mr-2" />
          <h3 className="text-lg font-semibold">ARGO Float Locations</h3>
          <span className="ml-auto text-sm text-gray-400">{floats.length} floats</span>
        </div>
      </div>
      
      <div className="flex-1 relative">
        {floats.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400">
              <MapPin className="w-8 h-8 mx-auto mb-2" />
              <p>No float data available</p>
            </div>
          </div>
        ) : (
          <MapContainer
            center={center}
            zoom={floats.length === 1 ? 4 : 2}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {floats.map((float) => {
              const [lon, lat] = float.geometry?.coordinates || [0, 0]
              const props = float.properties || {}
              return (
                <Marker
                  key={props.id || float.geometry?.coordinates?.join(',')}
                  position={[lat, lon]}
                  icon={argoIcon}
                >
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <h3 className="font-semibold text-blue-900 mb-2">
                        {props.name || 'ARGO Float'}
                      </h3>
                      <p className="text-sm text-gray-600 mb-1">
                        <strong>Float ID:</strong> {props.id || 'Unknown'}
                      </p>
                      <p className="text-sm text-gray-600 mb-1">
                        <strong>Status:</strong>{' '}
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          props.status === 'active' 
                            ? 'bg-green-600 text-white' 
                            : 'bg-yellow-600 text-white'
                        }`}>
                          {props.status || 'Unknown'}
                        </span>
                      </p>
                      {props.total_profiles && (
                        <p className="text-sm text-gray-600 mb-1">
                          <strong>Profiles:</strong> {props.total_profiles}
                        </p>
                      )}
                      {props.last_update && (
                        <p className="text-sm text-gray-600 mb-1">
                          <strong>Last Update:</strong> {new Date(props.last_update).toLocaleDateString()}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        Position: {lat.toFixed(2)}°N, {lon.toFixed(2)}°E
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )
            })}
          </MapContainer>
        )}
      </div>
    </div>
  )
}
