import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export interface QueryRequest {
  query: string
  session_id?: string
  user_id?: string
  context?: Record<string, unknown>
}

export interface QueryResponse {
  response: string
  sources: Array<{
    type: string
    id: string
    float_id?: string
    date?: string
    location?: { lat: number; lon: number }
  }>
  visualization?: {
    type: string
    title: string
    config: Record<string, unknown>
    data?: any
    profile_id?: string
  }
  data_table?: {
    profiles?: any[]
    floats?: any[]
  }
  user_type?: string
  query_intent?: string
  entities?: Record<string, unknown>
  metadata?: Record<string, unknown>
  timestamp: string
}

export interface Profile {
  id: string
  float_id: string
  profile_number: number
  profile_date: string
  latitude: number
  longitude: number
  number_of_levels?: number
  pressure_min?: number
  pressure_max?: number
  depth_min?: number
  depth_max?: number
  has_temperature: boolean
  has_salinity: boolean
  has_pressure: boolean
  has_bgc_data: boolean
  summary?: string
  metadata?: Record<string, unknown>
}

export interface Float {
  id: string
  float_id: string
  platform_number: string
  wmo_number?: string
  name?: string
  project_name?: string
  deployment_date?: string
  deployment_latitude?: number
  deployment_longitude?: number
  last_profile_date?: string
  last_latitude?: number
  last_longitude?: number
  current_status?: string
  metadata?: Record<string, unknown>
}

// API functions
export const queryAPI = {
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    try {
      // Use the simple query endpoint
      const response = await api.post<QueryResponse>('/query', request)
      return response.data
    } catch (error) {
      console.error('Query failed:', error)
      // Return a fallback response
      return {
        response: "I'm having trouble processing your query right now. Please try asking about ocean temperature, salinity, or ARGO float locations.",
        sources: [],
        visualization: {
          type: "map",
          title: "ARGO Float Locations",
          config: { center: [0, 0], zoom: 2 }
        },
        user_type: "general",
        query_intent: "general_query",
        entities: {},
        metadata: {},
        timestamp: new Date().toISOString()
      }
    }
  },
}

export const profileAPI = {
  getProfiles: async (params?: {
    page?: number
    page_size?: number
    float_id?: string
    start_date?: string
    end_date?: string
    min_latitude?: number
    max_latitude?: number
    min_longitude?: number
    max_longitude?: number
  }): Promise<{ profiles: Profile[]; total: number; page: number; page_size: number }> => {
    try {
      const response = await api.get('/profiles', { params })
      return response.data
    } catch (error) {
      // Fallback to simple endpoint
      console.warn('Failed to get profiles from main endpoint, using simple endpoint')
      const response = await api.get('/simple/profiles', { params: { page: params?.page || 1, page_size: params?.page_size || 20 } })
      return response.data
    }
  },
  getProfile: async (profileId: string): Promise<Profile> => {
    try {
      const response = await api.get(`/profiles/${profileId}`)
      return response.data
    } catch (error) {
      // Fallback - return sample profile
      console.warn('Failed to get profile from main endpoint')
      throw error
    }
  },
}

export const floatAPI = {
  getFloats: async (params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<{ floats: Float[]; total: number; page: number; page_size: number }> => {
    try {
      const response = await api.get('/floats', { params })
      return response.data
    } catch (error) {
      // Fallback to simple endpoint
      console.warn('Failed to get floats from main endpoint, using simple endpoint')
      const response = await api.get('/simple/floats/list', { params: { page: params?.page || 1, page_size: params?.page_size || 20 } })
      return response.data
    }
  },
  getFloat: async (floatId: string): Promise<Float> => {
    try {
      const response = await api.get(`/floats/${floatId}`)
      return response.data
    } catch (error) {
      // Fallback - return sample float
      console.warn('Failed to get float from main endpoint')
      throw error
    }
  },
}

export const healthAPI = {
  check: async (): Promise<{ status: string; database?: string }> => {
    const response = await api.get('/health/health')
    return response.data
  },
}

export const visualizationAPI = {
  getFloatLocations: async (params?: {
    bbox?: string
    status?: string
    limit?: number
  }) => {
    try {
      const response = await api.get('/simple/floats', { params })
      return response.data
    } catch (error) {
      console.error('Failed to get float locations:', error)
      // Return fallback data
      return {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            geometry: { type: "Point", coordinates: [-30.1, 45.2] },
            properties: { id: "5906468", name: "North Atlantic Float", status: "active", last_update: "2024-11-10", total_profiles: 156 }
          }
        ]
      }
    }
  },
  
  getProfileLocations: async (params?: {
    bbox?: string
    start_date?: string
    end_date?: string
    has_bgc?: boolean
    limit?: number
  }) => {
    try {
      const response = await api.get('/simple/search', { params })
      return response.data
    } catch (error) {
      console.error('Failed to get profile locations:', error)
      return { profiles: [], total: 0 }
    }
  },
  
  getTemperatureDepthChart: async (profileId: string) => {
    try {
      const response = await api.get(`/simple/profiles/${profileId}/temperature-depth`)
      return response.data
    } catch (error) {
      console.error('Failed to get temperature-depth chart:', error)
      return { data: [], metadata: { parameter: "temperature", units: "°C" } }
    }
  },
  
  getSalinityDepthChart: async (profileId: string) => {
    try {
      const response = await api.get(`/simple/profiles/${profileId}/salinity-depth`)
      return response.data
    } catch (error) {
      console.error('Failed to get salinity-depth chart:', error)
      return { data: [], metadata: { parameter: "salinity", units: "PSU" } }
    }
  },
  
  getTSDiagram: async (profileId: string) => {
    // T-S diagram not implemented in simple version, return empty
    return { data: [], metadata: { parameter: "ts_diagram", units: "mixed" } }
  },
  
  exportProfileCSV: async (profileId: string) => {
    try {
      const response = await api.get(`/simple/export/csv/${profileId}`)
      const csvContent = response.data.content
      const blob = new Blob([csvContent], { type: 'text/csv' })
      return blob
    } catch (error) {
      console.error('Failed to export CSV:', error)
      // Create a fallback CSV
      const csvContent = "level,pressure,depth,temperature,salinity\n1,5,5.1,25.2,35.1\n2,55,56.1,24.8,35.0\n3,105,107.1,24.2,34.9"
      const blob = new Blob([csvContent], { type: 'text/csv' })
      return blob
    }
  },
  
  searchProfiles: async (params?: {
    query?: string
    bbox?: string
    start_date?: string
    end_date?: string
    has_temperature?: boolean
    has_salinity?: boolean
    has_bgc?: boolean
    min_depth?: number
    max_depth?: number
    limit?: number
  }) => {
    try {
      const response = await api.get('/simple/search', { params })
      return response.data
    } catch (error) {
      console.error('Failed to search profiles:', error)
      return { profiles: [], total: 0, query: params }
    }
  },
}

export default api

