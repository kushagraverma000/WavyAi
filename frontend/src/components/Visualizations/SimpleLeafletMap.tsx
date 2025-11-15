import React, { useEffect, useState } from 'react'
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

interface FloatData {
  type: string
  geometry: {
    type: string
    coordinates: [number, number]
  }
  properties: {
    id: string
    name: string
    status: string
    last_update: string
    total_profiles: number
  }
}

interface SimpleLeafletMapProps {
  floats?: FloatData[]
  center?: [number, number]
  zoom?: number
  height?: string
}

const SimpleLeafletMap: React.FC<SimpleLeafletMapProps> = ({
  floats = [],
  center = [20, 0],
  zoom = 2,
  height = '400px'
}) => {
  const [mapData, setMapData] = useState<FloatData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFloatData = async () => {
      try {
        if (floats.length > 0) {
          setMapData(floats)
        } else {
          // Fetch from API
          const response = await fetch('/api/v1/simple/floats')
          const data = await response.json()
          setMapData(data.features || [])
        }
      } catch (error) {
        console.error('Failed to fetch float data:', error)
        // Use fallback data
        setMapData([
          {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [-30.1, 45.2]
            },
            properties: {
              id: '5906468',
              name: 'North Atlantic Float',
              status: 'active',
              last_update: '2024-11-10',
              total_profiles: 156
            }
          },
          {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [-140.2, 0.5]
            },
            properties: {
              id: '5906469',
              name: 'Pacific Equatorial Float',
              status: 'active',
              last_update: '2024-11-12',
              total_profiles: 142
            }
          },
          {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [85.4, -55.3]
            },
            properties: {
              id: '5906470',
              name: 'Southern Ocean Float',
              status: 'active',
              last_update: '2024-11-08',
              total_profiles: 168
            }
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchFloatData()
  }, [floats])

  // Custom icon for ARGO floats
  const argoIcon = new L.Icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="8" fill="#0ea5e9" stroke="#0284c7" stroke-width="2"/>
        <circle cx="12" cy="12" r="3" fill="white"/>
      </svg>
    `),
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <div className="text-gray-600">Loading map...</div>
      </div>
    )
  }

  return (
    <div className="w-full rounded-lg overflow-hidden border border-gray-200">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height, width: '100%' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {mapData.map((float) => {
          const [lon, lat] = float.geometry.coordinates
          return (
            <Marker
              key={float.properties.id}
              position={[lat, lon]}
              icon={argoIcon}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold text-blue-900">
                    {float.properties.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Float ID: {float.properties.id}
                  </p>
                  <p className="text-sm text-gray-600">
                    Status: <span className="capitalize">{float.properties.status}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Profiles: {float.properties.total_profiles}
                  </p>
                  <p className="text-sm text-gray-600">
                    Last Update: {float.properties.last_update}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Position: {lat.toFixed(2)}°, {lon.toFixed(2)}°
                  </p>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}

export default SimpleLeafletMap
