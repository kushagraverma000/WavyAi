import { Info, User, Target, Database, ExternalLink } from 'lucide-react'
import { useStore } from '../../store/useStore'

export default function ContextPanel() {
  const { currentQuery, userType, queryHistory } = useStore()

  return (
    <div className="flex flex-col h-full bg-ocean-medium">
      {/* Header */}
      <div className="p-4 border-b border-ocean-light">
        <h2 className="text-xl font-bold flex items-center space-x-2">
          <Info className="w-6 h-6 text-ocean-turquoise" />
          <span>Context</span>
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* User Type */}
        {userType && (
          <div className="card">
            <div className="flex items-center space-x-2 mb-2">
              <User className="w-5 h-5 text-ocean-turquoise" />
              <h3 className="font-semibold">User Type</h3>
            </div>
            <p className="text-sm text-gray-300 capitalize">{userType}</p>
          </div>
        )}

        {/* Query Intent */}
        {currentQuery?.query_intent && (
          <div className="card">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-5 h-5 text-ocean-turquoise" />
              <h3 className="font-semibold">Query Intent</h3>
            </div>
            <p className="text-sm text-gray-300 capitalize">
              {currentQuery.query_intent.replace('_', ' ')}
            </p>
          </div>
        )}

        {/* Sources */}
        {currentQuery?.sources && currentQuery.sources.length > 0 && (
          <div className="card">
            <div className="flex items-center space-x-2 mb-2">
              <Database className="w-5 h-5 text-ocean-turquoise" />
              <h3 className="font-semibold">Data Sources</h3>
            </div>
            <div className="space-y-2">
              {currentQuery.sources.slice(0, 5).map((source, index) => (
                <div key={index} className="text-sm text-gray-300">
                  <p className="font-medium">{source.type}</p>
                  {source.date && <p className="text-xs">{source.date}</p>}
                  {source.location && (
                    <p className="text-xs">
                      {source.location.lat.toFixed(2)}, {source.location.lon.toFixed(2)}
                    </p>
                  )}
                </div>
              ))}
              {currentQuery.sources.length > 5 && (
                <p className="text-xs text-gray-400">
                  +{currentQuery.sources.length - 5} more sources
                </p>
              )}
            </div>
          </div>
        )}

        {/* Entities */}
        {currentQuery?.entities && (
          <div className="card">
            <h3 className="font-semibold mb-2">Extracted Entities</h3>
            <div className="space-y-2 text-sm">
              {currentQuery.entities.parameters && (
                <div>
                  <p className="font-medium text-gray-300">Parameters:</p>
                  <p className="text-gray-400">
                    {Array.isArray(currentQuery.entities.parameters)
                      ? currentQuery.entities.parameters.join(', ')
                      : String(currentQuery.entities.parameters)}
                  </p>
                </div>
              )}
              {currentQuery.entities.depth_ranges && (
                <div>
                  <p className="font-medium text-gray-300">Depth Ranges:</p>
                  <p className="text-gray-400">
                    {Array.isArray(currentQuery.entities.depth_ranges)
                      ? currentQuery.entities.depth_ranges.join(', ') + ' m'
                      : String(currentQuery.entities.depth_ranges)}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="card">
          <h3 className="font-semibold mb-2">Session Statistics</h3>
          <div className="space-y-2 text-sm text-gray-300">
            <p>Total Queries: {queryHistory.length}</p>
            {currentQuery?.metadata && currentQuery.metadata.confidence && (
              <p>Confidence: {(currentQuery.metadata.confidence * 100).toFixed(0)}%</p>
            )}
          </div>
        </div>

        {/* Export Options */}
        {currentQuery && (
          <div className="card">
            <h3 className="font-semibold mb-2">Export</h3>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 bg-ocean-turquoise text-ocean-deep rounded-lg hover:bg-opacity-90 transition-colors text-sm">
                Download CSV
              </button>
              <button className="w-full px-4 py-2 bg-ocean-light text-white rounded-lg hover:bg-opacity-90 transition-colors text-sm">
                Download JSON
              </button>
              <button className="w-full px-4 py-2 bg-ocean-light text-white rounded-lg hover:bg-opacity-90 transition-colors text-sm flex items-center justify-center space-x-2">
                <span>Share</span>
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

