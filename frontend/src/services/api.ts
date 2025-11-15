// NOTE: This file is now a pure frontend mock layer.
// It returns hardcoded demo data and does not make any HTTP requests.

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

// API functions
export const queryAPI = {
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const now = new Date().toISOString()

    return {
      response:
        request.query ||
        'Exploring the global ocean with ARGO floats. This is a demo answer generated entirely on the frontend.',
      sources: [
        {
          type: 'float_profile',
          id: 'profile-1',
          float_id: '5906468',
          date: '2024-11-10T00:00:00Z',
          location: { lat: 45.2, lon: -30.1 },
        },
        {
          type: 'float_profile',
          id: 'profile-2',
          float_id: '5905123',
          date: '2024-10-02T00:00:00Z',
          location: { lat: -55.2, lon: 142.1 },
        },
      ],
      visualization: {
        type: 'map',
        title: 'Demo ARGO Float Locations',
        config: { center: [10, 0], zoom: 2 },
        data: {
          floats: MOCK_FLOATS,
        },
      },
      data_table: {
        profiles: MOCK_PROFILES,
        floats: MOCK_FLOATS,
      },
      user_type: 'ocean_scientist',
      query_intent: 'explore_argo_profiles',
      entities: {
        region: ['North Atlantic', 'Southern Ocean'],
        variables: ['temperature', 'salinity'],
      },
      metadata: {
        demo: true,
      },
      timestamp: now,
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
    const page = params?.page ?? 1
    const page_size = params?.page_size ?? MOCK_PROFILES.length

    return {
      profiles: MOCK_PROFILES,
      total: MOCK_PROFILES.length,
      page,
      page_size,
    }
  },
  getProfile: async (profileId: string): Promise<Profile> => {
    const profile = MOCK_PROFILES.find((p) => p.id === profileId || p.float_id === profileId)
    return (
      profile || {
        ...MOCK_PROFILES[0],
        id: profileId,
      }
    )
  },
}

export const floatAPI = {
  getFloats: async (params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<{ floats: Float[]; total: number; page: number; page_size: number }> => {
    const page = params?.page ?? 1
    const page_size = params?.page_size ?? MOCK_FLOATS.length

    return {
      floats: MOCK_FLOATS,
      total: MOCK_FLOATS.length,
      page,
      page_size,
    }
  },
  getFloat: async (floatId: string): Promise<Float> => {
    const item = MOCK_FLOATS.find((f) => f.id === floatId || f.float_id === floatId)
    return (
      item || {
        ...MOCK_FLOATS[0],
        id: floatId,
      }
    )
  },
}

export const healthAPI = {
  check: async (): Promise<{ status: string; database?: string }> => {
    return Promise.resolve({ status: 'healthy', database: 'mock' })
  },
}

export const visualizationAPI = {
  getFloatLocations: async (params?: {
    bbox?: string
    status?: string
    limit?: number
  }) => {
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
  },
  
  getProfileLocations: async (params?: {
    bbox?: string
    start_date?: string
    end_date?: string
    has_bgc?: boolean
    limit?: number
  }) => {
    return {
      profiles: MOCK_PROFILES,
      total: MOCK_PROFILES.length,
      query: params,
    }
  },
  
  getTemperatureDepthChart: async (profileId: string) => {
    const data = Array.from({ length: 20 }).map((_, i) => ({
      depth: i * 100,
      temperature: 25 - i * 0.4,
    }))

    return { data, metadata: { parameter: 'temperature', units: '°C' } }
  },
  
  getSalinityDepthChart: async (profileId: string) => {
    const data = Array.from({ length: 20 }).map((_, i) => ({
      depth: i * 100,
      salinity: 35 - i * 0.02,
    }))

    return { data, metadata: { parameter: 'salinity', units: 'PSU' } }
  },
  
  getTSDiagram: async (_profileId: string) => {
    // T-S diagram not implemented in simple version, return empty
    return { data: [], metadata: { parameter: "ts_diagram", units: "mixed" } }
  },
  
  exportProfileCSV: async (profileId: string) => {
    const csvContent =
      'level,pressure,depth,temperature,salinity\n' +
      '1,5,5.1,25.2,35.1\n' +
      '2,55,56.1,24.8,35.0\n' +
      '3,105,107.1,24.2,34.9'
    const blob = new Blob([csvContent], { type: 'text/csv' })
    return blob
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
    return {
      profiles: MOCK_PROFILES,
      total: MOCK_PROFILES.length,
      query: params,
    }
  },
}

// No default export (axios instance) is needed in the mock-only version.

