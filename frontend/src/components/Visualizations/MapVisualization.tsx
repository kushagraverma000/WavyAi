import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { QueryResponse, visualizationAPI } from '../../services/api'

interface MapVisualizationProps {
  query: QueryResponse | null
}

export default function MapVisualization({ query }: MapVisualizationProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [mapboxToken] = useState(import.meta.env.VITE_MAPBOX_TOKEN || '')
  const [floats, setFloats] = useState<any[]>([])

  useEffect(() => {
    if (!mapContainer.current || !mapboxToken) return

    // Initialize map
    if (!map.current) {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [0, 30],
        zoom: 2,
        accessToken: mapboxToken,
      })
    }

    // Load floats
    visualizationAPI
      .getFloatLocations({ limit: 100 })
      .then((data: any) => {
        const floatFeatures = data.features || []
        setFloats(floatFeatures)
        // Add floats to map after map is initialized
        setTimeout(() => {
          addFloatsToMap(floatFeatures)
        }, 1000)
      })
      .catch((error: any) => {
        console.error('Failed to load floats:', error)
      })
  }, [mapboxToken])

  const addFloatsToMap = (floatData: any[]) => {
    if (!map.current) return

    // Remove existing markers
    const markers = document.querySelectorAll('.float-marker')
    markers.forEach((marker) => marker.remove())

    // Add markers for each float (GeoJSON features)
    floatData.forEach((feature) => {
      try {
        if (feature.geometry && feature.geometry.coordinates) {
          const [lon, lat] = feature.geometry.coordinates
          const props = feature.properties || {}
          
          if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
            const el = document.createElement('div')
            el.className = 'float-marker'
            el.style.width = '12px'
            el.style.height = '12px'
            el.style.borderRadius = '50%'
            el.style.backgroundColor = '#1EE3CF'
            el.style.border = '2px solid #0A1128'
            el.style.cursor = 'pointer'

            new mapboxgl.Marker(el)
              .setLngLat([lon, lat])
              .setPopup(
                new mapboxgl.Popup().setHTML(`
                  <div class="text-black">
                    <h3 class="font-bold">${props.float_id || props.platform_number || 'Unknown'}</h3>
                    <p class="text-sm">Status: ${props.status || 'Unknown'}</p>
                    <p class="text-sm">Last Profile: ${props.last_profile_date || 'N/A'}</p>
                  </div>
                `)
              )
              .addTo(map.current!)
          }
        }
      } catch (error) {
        console.error('Failed to add float marker:', error, feature)
      }
    })

    // Add sources from query if available
    if (query?.sources) {
      query.sources.forEach((source) => {
        try {
          if (source.location && source.location.lat && source.location.lon) {
            const el = document.createElement('div')
            el.className = 'source-marker'
            el.style.width = '10px'
            el.style.height = '10px'
            el.style.borderRadius = '50%'
            el.style.backgroundColor = '#FF6B6B'
            el.style.border = '2px solid #0A1128'
            el.style.cursor = 'pointer'

            new mapboxgl.Marker(el)
              .setLngLat([source.location.lon, source.location.lat])
              .setPopup(
                new mapboxgl.Popup().setHTML(`
                  <div class="text-black">
                    <h3 class="font-bold">Data Source</h3>
                    <p class="text-sm">Type: ${source.type || 'Unknown'}</p>
                    <p class="text-sm">Date: ${source.date || 'N/A'}</p>
                  </div>
                `)
              )
              .addTo(map.current!)
          }
        } catch (error) {
          console.error('Failed to add source marker:', error, source)
        }
      })
    }
  }

  useEffect(() => {
    if (query?.sources && map.current && floats.length > 0) {
      addFloatsToMap(floats)
    }
  }, [query, floats])

  if (!mapboxToken) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">Mapbox token not configured</p>
      </div>
    )
  }

  return <div ref={mapContainer} className="w-full h-full" />
}

