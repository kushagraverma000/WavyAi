// NOTE: This file is now a pure frontend mock layer.
// It returns hardcoded demo data and does not make any HTTP requests.

export interface QueryRequest {
  query?: string
  session_id?: string
  user_id?: string
  selected_date?: string
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

// Mock data
const MOCK_FLOATS: Float[] = [
  {
    id: 'float-1',
    float_id: '5906468',
    platform_number: 'NA-001',
    name: 'North Atlantic Float',
    project_name: 'WavyAI Demo Mission',
    deployment_date: '2024-01-15T00:00:00Z',
    deployment_latitude: 45.2,
    deployment_longitude: -30.1,
    last_profile_date: '2024-11-10T00:00:00Z',
    last_latitude: 45.2,
    last_longitude: -30.1,
    current_status: 'active',
    metadata: { region: 'North Atlantic', cycles: 156 },
  },
  {
    id: 'float-2',
    float_id: '5905123',
    platform_number: 'SO-014',
    name: 'Southern Ocean Float',
    project_name: 'Deep Waters Campaign',
    deployment_date: '2023-09-03T00:00:00Z',
    deployment_latitude: -55.8,
    deployment_longitude: 140.3,
    last_profile_date: '2024-10-02T00:00:00Z',
    last_latitude: -55.2,
    last_longitude: 142.1,
    current_status: 'active',
    metadata: { region: 'Southern Ocean', cycles: 98 },
  },
]

const MOCK_PROFILES: Profile[] = [
  {
    id: 'profile-1',
    float_id: '5906468',
    profile_number: 156,
    profile_date: '2024-11-10T00:00:00Z',
    latitude: 45.2,
    longitude: -30.1,
    number_of_levels: 120,
    pressure_min: 5,
    pressure_max: 2000,
    depth_min: 5,
    depth_max: 2000,
    has_temperature: true,
    has_salinity: true,
    has_pressure: true,
    has_bgc_data: true,
    summary: 'Latest profile from the North Atlantic demonstration float.',
    metadata: { region: 'North Atlantic' },
  },
  {
    id: 'profile-2',
    float_id: '5905123',
    profile_number: 98,
    profile_date: '2024-10-02T00:00:00Z',
    latitude: -55.2,
    longitude: 142.1,
    number_of_levels: 95,
    pressure_min: 5,
    pressure_max: 1500,
    depth_min: 5,
    depth_max: 1500,
    has_temperature: true,
    has_salinity: true,
    has_pressure: true,
    has_bgc_data: false,
    summary: 'Southern Ocean profile highlighting the Antarctic Circumpolar Current.',
    metadata: { region: 'Southern Ocean' },
  },
]

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1"

// API functions
export const queryAPI = {
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    })
    if (!response.ok) {
      throw new Error(`Query API failed with status ${response.status}`)
    }
    const data = (await response.json()) as QueryResponse
    return data
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
    const query = new URLSearchParams()
    if (params?.page) query.append('page', String(params.page))
    if (params?.page_size) query.append('page_size', String(params.page_size))
    if (params?.float_id) query.append('float_id', params.float_id)
    if (params?.start_date) query.append('start_date', params.start_date)
    if (params?.end_date) query.append('end_date', params.end_date)
    if (params?.min_latitude !== undefined) query.append('min_latitude', String(params.min_latitude))
    if (params?.max_latitude !== undefined) query.append('max_latitude', String(params.max_latitude))
    if (params?.min_longitude !== undefined) query.append('min_longitude', String(params.min_longitude))
    if (params?.max_longitude !== undefined) query.append('max_longitude', String(params.max_longitude))

    const url = `${API_BASE}/profiles${query.toString() ? `?${query.toString()}` : ''}`

    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`getProfiles failed with status ${response.status}`)
      }
      const data = (await response.json()) as { profiles: Profile[]; total: number; page: number; page_size: number }
      return data
    } catch (error) {
      console.error('profileAPI.getProfiles failed, falling back to mock data:', error)
      const page = params?.page ?? 1
      const page_size = params?.page_size ?? MOCK_PROFILES.length
      return {
        profiles: MOCK_PROFILES,
        total: MOCK_PROFILES.length,
        page,
        page_size,
      }
    }
  },
  getProfile: async (profileId: string): Promise<Profile> => {
    try {
      const response = await fetch(`${API_BASE}/profiles/${encodeURIComponent(profileId)}`)
      if (!response.ok) {
        throw new Error(`getProfile failed with status ${response.status}`)
      }
      return (await response.json()) as Profile
    } catch (error) {
      console.error('profileAPI.getProfile failed, falling back to mock data:', error)
      const profile = MOCK_PROFILES.find((p) => p.id === profileId || p.float_id === profileId)
      return (
        profile || {
          ...MOCK_PROFILES[0],
          id: profileId,
        }
      )
    }
  },
}

export const floatAPI = {
  getFloats: async (params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<{ floats: Float[]; total: number; page: number; page_size: number }> => {
    const query = new URLSearchParams()
    if (params?.page) query.append('page', String(params.page))
    if (params?.page_size) query.append('page_size', String(params.page_size))
    if (params?.status) query.append('status', params.status)

    const url = `${API_BASE}/floats${query.toString() ? `?${query.toString()}` : ''}`

    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`getFloats failed with status ${response.status}`)
      }
      const data = (await response.json()) as { floats: Float[]; total: number; page: number; page_size: number }
      return data
    } catch (error) {
      console.error('floatAPI.getFloats failed, falling back to mock data:', error)
      const page = params?.page ?? 1
      const page_size = params?.page_size ?? MOCK_FLOATS.length
      return {
        floats: MOCK_FLOATS,
        total: MOCK_FLOATS.length,
        page,
        page_size,
      }
    }
  },
  getFloat: async (floatId: string): Promise<Float> => {
    try {
      const response = await fetch(`${API_BASE}/floats/${encodeURIComponent(floatId)}`)
      if (!response.ok) {
        throw new Error(`getFloat failed with status ${response.status}`)
      }
      return (await response.json()) as Float
    } catch (error) {
      console.error('floatAPI.getFloat failed, falling back to mock data:', error)
      const item = MOCK_FLOATS.find((f) => f.id === floatId || f.float_id === floatId)
      return (
        item || {
          ...MOCK_FLOATS[0],
          id: floatId,
        }
      )
    }
  },
}

export const healthAPI = {
  check: async (): Promise<{ status: string; database?: string }> => {
    try {
      const apiBase = API_BASE
      const root = apiBase.replace(/\/api\/v1\/?$/, '')
      const url = root ? `${root}/health` : '/health'
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Health check failed with status ${response.status}`)
      }
      const data = (await response.json()) as { status: string; database?: string }
      return data
    } catch (error) {
      console.error('healthAPI.check failed, returning mock status:', error)
      return { status: 'unreachable', database: 'unknown' }
    }
  },
}

export const visualizationAPI = {
  getFloatLocations: async (params?: {
    bbox?: string
    status?: string
    limit?: number
    day?: string
  }) => {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', String(params.limit))
    if (params?.status) query.append('status', params.status)
    if (params?.day) query.append('day', params.day)

    const url = `${API_BASE}/visualization/float-locations${query.toString() ? `?${query.toString()}` : ''}`

    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`getFloatLocations failed with status ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('visualizationAPI.getFloatLocations failed, falling back to mock data:', error)
      return {
        type: 'FeatureCollection',
        features: MOCK_FLOATS.map((f) => ({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [f.last_longitude ?? f.deployment_longitude ?? 0, f.last_latitude ?? f.deployment_latitude ?? 0],
          },
          properties: {
            id: f.float_id,
            name: f.name,
            status: f.current_status,
            last_update: f.last_profile_date,
            total_profiles: (f.metadata as any)?.cycles ?? 0,
          },
        })),
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
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', String(params.limit))
    if (params?.bbox) query.append('bbox', params.bbox)
    if (params?.start_date) query.append('start_date', params.start_date)
    if (params?.end_date) query.append('end_date', params.end_date)
    if (params?.has_bgc !== undefined) query.append('has_bgc', String(params.has_bgc))

    const url = `${API_BASE}/visualization/profile-locations${query.toString() ? `?${query.toString()}` : ''}`

    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`getProfileLocations failed with status ${response.status}`)
      }
      const data = await response.json()
      return data
    } catch (error) {
      console.error('visualizationAPI.getProfileLocations failed, falling back to mock data:', error)
      return {
        profiles: MOCK_PROFILES,
        total: MOCK_PROFILES.length,
        query: params,
      }
    }
  },
  
  getTemperatureDepthChart: async (profileId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/visualization/profiles/${encodeURIComponent(profileId)}/temperature-depth`
      )
      if (!response.ok) {
        throw new Error(`getTemperatureDepthChart failed with status ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('visualizationAPI.getTemperatureDepthChart failed, falling back to mock data:', error)
      const data = Array.from({ length: 20 }).map((_, i) => ({
        depth: i * 100,
        temperature: 25 - i * 0.4,
      }))

      return { data, metadata: { parameter: 'temperature', units: '°C' } }
    }
  },
  
  getSalinityDepthChart: async (profileId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/visualization/profiles/${encodeURIComponent(profileId)}/salinity-depth`
      )
      if (!response.ok) {
        throw new Error(`getSalinityDepthChart failed with status ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('visualizationAPI.getSalinityDepthChart failed, falling back to mock data:', error)
      const data = Array.from({ length: 20 }).map((_, i) => ({
        depth: i * 100,
        salinity: 35 - i * 0.02,
      }))

      return { data, metadata: { parameter: 'salinity', units: 'PSU' } }
    }
  },
  
  getTSDiagram: async (_profileId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/visualization/profiles/${encodeURIComponent(_profileId)}/ts-diagram`
      )
      if (!response.ok) {
        throw new Error(`getTSDiagram failed with status ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('visualizationAPI.getTSDiagram failed, falling back to empty data:', error)
      return { data: [], metadata: { parameter: 'ts_diagram', units: 'mixed' } }
    }
  },
  
  exportProfileCSV: async (profileId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/profiles/${encodeURIComponent(profileId)}/export/csv`
      )
      if (!response.ok) {
        throw new Error(`exportProfileCSV failed with status ${response.status}`)
      }
      const blob = await response.blob()
      return blob
    } catch (error) {
      console.error('visualizationAPI.exportProfileCSV failed, falling back to mock CSV:', error)
      const csvContent =
        'level,pressure,depth,temperature,salinity\n' +
        '1,5,5.1,25.2,35.1\n' +
        '2,55,56.1,24.8,35.0\n' +
        '3,105,107.1,24.2,34.9'
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
      // Reuse profiles endpoint and adapt shape for chart components
      const page_size = params?.limit ?? 20
      const response = await profileAPI.getProfiles({ page: 1, page_size })
      const profilesWithId = response.profiles.map((p: any) => ({
        ...p,
        profile_id: p.id,
      }))

      return {
        profiles: profilesWithId,
        total: response.total,
        query: params,
      }
    } catch (error) {
      console.error('visualizationAPI.searchProfiles failed, falling back to mock data:', error)
      const profilesWithId = MOCK_PROFILES.map((p: any) => ({ ...p, profile_id: p.id }))
      return {
        profiles: profilesWithId,
        total: profilesWithId.length,
        query: params,
      }
    }
  },

  getDayDepthProfile: async (day: string, profileIndex: number = 0) => {
    const query = new URLSearchParams()
    query.append('day', day)
    query.append('profile_index', String(profileIndex))

    const url = `${API_BASE}/visualization/day/depth-profile?${query.toString()}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`getDayDepthProfile failed with status ${response.status}`)
    }
    return await response.json()
  },

  exportDayCSV: async (day: string): Promise<Blob> => {
    const query = new URLSearchParams()
    query.append('day', day)
    const url = `${API_BASE}/export/day-csv?${query.toString()}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`exportDayCSV failed with status ${response.status}`)
    }
    return await response.blob()
  },

  exportDayNetCDF: async (day: string): Promise<Blob> => {
    const query = new URLSearchParams()
    query.append('day', day)
    const url = `${API_BASE}/export/day-netcdf?${query.toString()}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`exportDayNetCDF failed with status ${response.status}`)
    }
    return await response.blob()
  },
}

// No default export (axios instance) is needed in the mock-only version.

