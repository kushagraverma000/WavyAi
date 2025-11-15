import { useState, useEffect } from 'react'
import { Search, Table, FileText, Database } from 'lucide-react'
import { profileAPI, floatAPI, visualizationAPI } from '../../services/api'

interface DataTablePanelProps {
  query: any
}

export default function DataTablePanel({ query }: DataTablePanelProps) {
  const [data, setData] = useState<any[]>([])
  const [filteredData, setFilteredData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  const [sortField, setSortField] = useState('')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [dataType, setDataType] = useState<'profiles' | 'floats'>('profiles')

  // Load data based on query
  useEffect(() => {
    // Use data from query response if available
    if (query?.data_table) {
      if (dataType === 'profiles' && query.data_table.profiles) {
        setData(query.data_table.profiles)
        setFilteredData(query.data_table.profiles)
      } else if (dataType === 'floats' && query.data_table.floats) {
        setData(query.data_table.floats)
        setFilteredData(query.data_table.floats)
      }
    } else if (query?.sources && query.sources.length > 0) {
      loadData()
    }
  }, [query, dataType])

  const loadData = async () => {
    setLoading(true)
    try {
      if (dataType === 'profiles') {
        const response = await profileAPI.getProfiles({ page_size: 100 })
        setData(response.profiles)
        setFilteredData(response.profiles)
      } else {
        const response = await floatAPI.getFloats({ page_size: 100 })
        setData(response.floats)
        setFilteredData(response.floats)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter and search data
  useEffect(() => {
    let filtered = [...data]

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(item => 
        Object.values(item).some(value => 
          value && value.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    // Apply sorting
    if (sortField) {
      filtered.sort((a, b) => {
        const aVal = a[sortField]
        const bVal = b[sortField]
        
        if (aVal === null || aVal === undefined) return 1
        if (bVal === null || bVal === undefined) return -1
        
        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
        return sortDirection === 'asc' ? comparison : -comparison
      })
    }

    setFilteredData(filtered)
    setCurrentPage(1)
  }, [data, searchTerm, sortField, sortDirection])

  // Pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage)

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const handleDownload = async (format: 'csv' | 'netcdf') => {
    try {
      // Use simple export endpoint for CSV
      if (format === 'csv') {
        const endpoint = dataType === 'profiles'
          ? '/api/v1/simple/export/profiles/csv'
          : '/api/v1/simple/export/profiles/csv' // For now, use profiles endpoint
        
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${endpoint}`
        
        // Create download link
        const link = document.createElement('a')
        link.href = url
        link.download = `${dataType}_${new Date().toISOString().split('T')[0]}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } else {
        // For NetCDF, try the regular export endpoint
        const params = new URLSearchParams()
        if (searchTerm) params.append('search', searchTerm)
        
        const endpoint = dataType === 'profiles' 
          ? `/api/v1/export/profiles/${format}`
          : `/api/v1/export/floats/${format}`
        
        const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${endpoint}?${params.toString()}`
        
        // Create download link
        const link = document.createElement('a')
        link.href = url
        link.download = `${dataType}_${new Date().toISOString().split('T')[0]}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    } catch (error) {
      console.error('Download failed:', error)
      // Fallback: create CSV from current data
      if (format === 'csv') {
        try {
          const csvContent = generateCSVFromData(filteredData)
          const blob = new Blob([csvContent], { type: 'text/csv' })
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `${dataType}_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(link)
          link.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(link)
        } catch (fallbackError) {
          console.error('Fallback CSV generation failed:', fallbackError)
        }
      }
    }
  }

  const generateCSVFromData = (data: any[]): string => {
    if (data.length === 0) return ''
    
    const headers = Object.keys(data[0])
    const csvRows = [headers.join(',')]
    
    for (const row of data) {
      const values = headers.map(header => {
        const value = row[header]
        if (value === null || value === undefined) return ''
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`
        }
        return String(value)
      })
      csvRows.push(values.join(','))
    }
    
    return csvRows.join('\n')
  }

  const renderProfilesTable = () => (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-ocean-medium">
          <tr>
            {[
              { key: 'float_id', label: 'Float ID' },
              { key: 'profile_number', label: 'Profile #' },
              { key: 'profile_date', label: 'Date' },
              { key: 'latitude', label: 'Latitude' },
              { key: 'longitude', label: 'Longitude' },
              { key: 'number_of_levels', label: 'Levels' },
              { key: 'has_temperature', label: 'Temp' },
              { key: 'has_salinity', label: 'Sal' },
              { key: 'has_bgc_data', label: 'BGC' },
            ].map(({ key, label }) => (
              <th
                key={key}
                className="px-4 py-3 text-left cursor-pointer hover:bg-ocean-light transition-colors"
                onClick={() => handleSort(key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{label}</span>
                  {sortField === key && (
                    <span className="text-ocean-turquoise">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((profile, index) => (
            <tr key={profile.id} className={index % 2 === 0 ? 'bg-ocean-deep' : 'bg-ocean-medium'}>
              <td className="px-4 py-3 font-mono text-xs">{profile.float_id}</td>
              <td className="px-4 py-3">{profile.profile_number}</td>
              <td className="px-4 py-3">{new Date(profile.profile_date).toLocaleDateString()}</td>
              <td className="px-4 py-3">{profile.latitude?.toFixed(3)}°N</td>
              <td className="px-4 py-3">{profile.longitude?.toFixed(3)}°E</td>
              <td className="px-4 py-3">{profile.number_of_levels || 'N/A'}</td>
              <td className="px-4 py-3">
                <span className={`w-3 h-3 rounded-full inline-block ${profile.has_temperature ? 'bg-green-500' : 'bg-gray-500'}`}></span>
              </td>
              <td className="px-4 py-3">
                <span className={`w-3 h-3 rounded-full inline-block ${profile.has_salinity ? 'bg-green-500' : 'bg-gray-500'}`}></span>
              </td>
              <td className="px-4 py-3">
                <span className={`w-3 h-3 rounded-full inline-block ${profile.has_bgc_data ? 'bg-green-500' : 'bg-gray-500'}`}></span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  const renderFloatsTable = () => (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-ocean-medium">
          <tr>
            {[
              { key: 'float_id', label: 'Float ID' },
              { key: 'platform_number', label: 'Platform' },
              { key: 'current_status', label: 'Status' },
              { key: 'deployment_date', label: 'Deployed' },
              { key: 'last_profile_date', label: 'Last Profile' },
              { key: 'last_latitude', label: 'Last Lat' },
              { key: 'last_longitude', label: 'Last Lon' },
            ].map(({ key, label }) => (
              <th
                key={key}
                className="px-4 py-3 text-left cursor-pointer hover:bg-ocean-light transition-colors"
                onClick={() => handleSort(key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{label}</span>
                  {sortField === key && (
                    <span className="text-ocean-turquoise">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((float, index) => (
            <tr key={float.id} className={index % 2 === 0 ? 'bg-ocean-deep' : 'bg-ocean-medium'}>
              <td className="px-4 py-3 font-mono text-xs">{float.float_id}</td>
              <td className="px-4 py-3">{float.platform_number}</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-1 rounded text-xs ${
                  float.current_status === 'active' ? 'bg-green-600 text-white' :
                  float.current_status === 'inactive' ? 'bg-yellow-600 text-white' :
                  'bg-gray-600 text-white'
                }`}>
                  {float.current_status || 'Unknown'}
                </span>
              </td>
              <td className="px-4 py-3">
                {float.deployment_date ? new Date(float.deployment_date).toLocaleDateString() : 'N/A'}
              </td>
              <td className="px-4 py-3">
                {float.last_profile_date ? new Date(float.last_profile_date).toLocaleDateString() : 'N/A'}
              </td>
              <td className="px-4 py-3">{float.last_latitude?.toFixed(3)}°N</td>
              <td className="px-4 py-3">{float.last_longitude?.toFixed(3)}°E</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  return (
    <div className="flex flex-col h-full bg-ocean-deep">
      {/* Header */}
      <div className="p-4 border-b border-ocean-medium">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold flex items-center space-x-2">
            <Table className="w-6 h-6 text-ocean-turquoise" />
            <span>Data Table</span>
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setDataType('profiles')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dataType === 'profiles'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-medium text-white hover:bg-ocean-light'
              }`}
            >
              Profiles
            </button>
            <button
              onClick={() => setDataType('floats')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dataType === 'floats'
                  ? 'bg-ocean-turquoise text-ocean-deep'
                  : 'bg-ocean-medium text-white hover:bg-ocean-light'
              }`}
            >
              Floats
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search data..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-ocean-medium text-white rounded-lg border border-ocean-light focus:outline-none focus:ring-2 focus:ring-ocean-turquoise"
              />
            </div>
          </div>

          {/* Download buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => handleDownload('csv')}
              className="px-4 py-2 bg-ocean-medium text-white rounded-lg hover:bg-ocean-light transition-colors flex items-center space-x-2"
            >
              <FileText className="w-4 h-4" />
              <span>CSV</span>
            </button>
            <button
              onClick={() => handleDownload('netcdf')}
              className="px-4 py-2 bg-ocean-medium text-white rounded-lg hover:bg-ocean-light transition-colors flex items-center space-x-2"
            >
              <Database className="w-4 h-4" />
              <span>NetCDF</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-4 text-sm text-gray-400">
          Showing {paginatedData.length} of {filteredData.length} {dataType}
          {searchTerm && ` (filtered from ${data.length} total)`}
        </div>
      </div>

      {/* Table Content */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ocean-turquoise"></div>
            <span className="ml-2 text-gray-400">Loading data...</span>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Table className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">No data available</p>
              <p className="text-sm text-gray-500 mt-2">
                Try adjusting your search criteria or query parameters
              </p>
            </div>
          </div>
        ) : (
          <>
            {dataType === 'profiles' ? renderProfilesTable() : renderFloatsTable()}
          </>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t border-ocean-medium">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-400">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-ocean-medium text-white rounded hover:bg-ocean-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 bg-ocean-medium text-white rounded hover:bg-ocean-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
