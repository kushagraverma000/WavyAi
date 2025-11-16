import { useEffect, useRef, useState } from 'react'
import { QueryResponse } from '../../services/api'
import { floatAPI } from '../../services/api'

interface GoogleMapVisualizationProps {
  query: QueryResponse | null
}

declare global {
  interface Window {
    google: any
    initMap: () => void
  }
}

export default function GoogleMapVisualization({ query }: GoogleMapVisualizationProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [googleMapsApiKey] = useState(import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '')
  const [floats, setFloats] = useState<any[]>([])
  const [isLoaded, setIsLoaded] = useState(false)

  // Load Google Maps API
  useEffect(() => {
    if (!googleMapsApiKey) return

    const loadGoogleMaps = () => {
      if (window.google) {
        setIsLoaded(true)
        return
      }

      window.initMap = () => {
        setIsLoaded(true)
      }

      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&callback=initMap`
      script.async = true
      script.defer = true
      document.head.appendChild(script)
    }

    loadGoogleMaps()
  }, [googleMapsApiKey])

  // Initialize map
  useEffect(() => {
    if (!isLoaded || !mapRef.current || mapInstanceRef.current) return

    mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
      center: { lat: 30, lng: 0 },
      zoom: 2,
      styles: [
        {
          "elementType": "geometry",
          "stylers": [{"color": "#1d2c4d"}]
        },
        {
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#8ec3b9"}]
        },
        {
          "elementType": "labels.text.stroke",
          "stylers": [{"color": "#1a3646"}]
        },
        {
          "featureType": "administrative.country",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#4b6878"}]
        },
        {
          "featureType": "administrative.land_parcel",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#64779e"}]
        },
        {
          "featureType": "administrative.province",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#4b6878"}]
        },
        {
          "featureType": "landscape.man_made",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#334e87"}]
        },
        {
          "featureType": "landscape.natural",
          "elementType": "geometry",
          "stylers": [{"color": "#023e58"}]
        },
        {
          "featureType": "poi",
          "elementType": "geometry",
          "stylers": [{"color": "#283d6a"}]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#6f9ba4"}]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text.stroke",
          "stylers": [{"color": "#1d2c4d"}]
        },
        {
          "featureType": "poi.park",
          "elementType": "geometry.fill",
          "stylers": [{"color": "#023e58"}]
        },
        {
          "featureType": "poi.park",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#3C7680"}]
        },
        {
          "featureType": "road",
          "elementType": "geometry",
          "stylers": [{"color": "#304a7d"}]
        },
        {
          "featureType": "road",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#98a5be"}]
        },
        {
          "featureType": "road",
          "elementType": "labels.text.stroke",
          "stylers": [{"color": "#1d2c4d"}]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry",
          "stylers": [{"color": "#2c6675"}]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#255763"}]
        },
        {
          "featureType": "road.highway",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#b0d5ce"}]
        },
        {
          "featureType": "road.highway",
          "elementType": "labels.text.stroke",
          "stylers": [{"color": "#023e58"}]
        },
        {
          "featureType": "transit",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#98a5be"}]
        },
        {
          "featureType": "transit",
          "elementType": "labels.text.stroke",
          "stylers": [{"color": "#1d2c4d"}]
        },
        {
          "featureType": "transit.line",
          "elementType": "geometry.fill",
          "stylers": [{"color": "#283d6a"}]
        },
        {
          "featureType": "transit.station",
          "elementType": "geometry",
          "stylers": [{"color": "#3a4762"}]
        },
        {
          "featureType": "water",
          "elementType": "geometry",
          "stylers": [{"color": "#0e1626"}]
        },
        {
          "featureType": "water",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#4e6d70"}]
        }
      ]
    })

    // Load floats data
    loadFloatsData()
  }, [isLoaded])

  // Load floats data
  const loadFloatsData = async () => {
    try {
      const data = await floatAPI.getFloats({ page_size: 100 })
      setFloats(data.floats)
      addFloatsToMap(data.floats)
    } catch (error) {
      console.error('Failed to load floats:', error)
    }
  }

  // Add floats to map
  const addFloatsToMap = (floatData: any[]) => {
    if (!mapInstanceRef.current) return

    floatData.forEach((float) => {
      try {
        const lat = float.last_latitude || float.deployment_latitude
        const lon = float.last_longitude || float.deployment_longitude
        
        if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
          const marker = new window.google.maps.Marker({
            position: { lat, lng: lon },
            map: mapInstanceRef.current,
            title: float.float_id || float.platform_number || 'Unknown',
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              fillColor: '#1EE3CF',
              fillOpacity: 0.8,
              strokeColor: '#0A1128',
              strokeWeight: 2,
              scale: 6,
            },
          })

          const infoWindow = new window.google.maps.InfoWindow({
            content: `
              <div style="color: #333; font-family: Arial, sans-serif;">
                <h3 style="margin: 0 0 8px 0; color: #1EE3CF;">${float.float_id || float.platform_number || 'Unknown'}</h3>
                <p style="margin: 4px 0;"><strong>Status:</strong> ${float.current_status || 'Unknown'}</p>
                <p style="margin: 4px 0;"><strong>Last Profile:</strong> ${float.last_profile_date || 'N/A'}</p>
                <p style="margin: 4px 0;"><strong>Location:</strong> ${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E</p>
              </div>
            `,
          })

          marker.addListener('click', () => {
            infoWindow.open(mapInstanceRef.current, marker)
          })
        }
      } catch (error) {
        console.error('Failed to add float marker:', error, float)
      }
    })

    // Add source markers from query if available
    if (query?.sources) {
      query.sources.forEach((source) => {
        try {
          if (source.location && source.location.lat && source.location.lon) {
            const marker = new window.google.maps.Marker({
              position: { lat: source.location.lat, lng: source.location.lon },
              map: mapInstanceRef.current,
              title: 'Data Source',
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                fillColor: '#FF6B6B',
                fillOpacity: 0.8,
                strokeColor: '#0A1128',
                strokeWeight: 2,
                scale: 5,
              },
            })

            const infoWindow = new window.google.maps.InfoWindow({
              content: `
                <div style="color: #333; font-family: Arial, sans-serif;">
                  <h3 style="margin: 0 0 8px 0; color: #FF6B6B;">Data Source</h3>
                  <p style="margin: 4px 0;"><strong>Type:</strong> ${source.type || 'Unknown'}</p>
                  <p style="margin: 4px 0;"><strong>Date:</strong> ${source.date || 'N/A'}</p>
                  <p style="margin: 4px 0;"><strong>Location:</strong> ${source.location.lat.toFixed(3)}°N, ${source.location.lon.toFixed(3)}°E</p>
                </div>
              `,
            })

            marker.addListener('click', () => {
              infoWindow.open(mapInstanceRef.current, marker)
            })
          }
        } catch (error) {
          console.error('Failed to add source marker:', error, source)
        }
      })
    }
  }

  // Update markers when query changes
  useEffect(() => {
    if (query?.sources && mapInstanceRef.current && floats.length > 0) {
      // Clear existing markers and re-add all
      addFloatsToMap(floats)
    }
  }, [query, floats])

  if (!googleMapsApiKey) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-400 mb-2">Google Maps API key not configured</p>
          <p className="text-sm text-gray-500">
            Please add VITE_GOOGLE_MAPS_API_KEY to your environment variables
          </p>
        </div>
      </div>
    )
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ocean-turquoise"></div>
        <span className="ml-2 text-gray-400">Loading Google Maps...</span>
      </div>
    )
  }

  return <div ref={mapRef} className="w-full h-full" />
}
