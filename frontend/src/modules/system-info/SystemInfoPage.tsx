import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { getSystemInfo } from '../../services/api'
import { 
  Monitor, 
  Cpu, 
  MemoryStick, 
  Clock, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  HardDrive
} from 'lucide-react'

interface SystemInfo {
  uptime: string
  cpu_usage: number
  memory_usage: {
    total: number
    used: number
    free: number
    percentage: number
  }
  disk_usage: {
    total: number
    used: number
    free: number
    percentage: number
  }
  load_average: number[]
  processes: number
  platform: string
  hostname: string
  timestamp: string
}

const SystemInfoPage: React.FC = () => {
  const { hasRole } = useAuth()
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    if (hasRole('admin')) {
      fetchSystemInfo()
    }
  }, [hasRole])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (autoRefresh && hasRole('admin')) {
      interval = setInterval(fetchSystemInfo, 5000) // Refresh every 5 seconds
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, hasRole])

  const fetchSystemInfo = async () => {
    try {
      setError(null)
      const data = await getSystemInfo()
      setSystemInfo(data)
    } catch (err) {
      setError('Failed to fetch system information')
      console.error('Error fetching system info:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatUptime = (uptime: string): string => {
    const seconds = parseInt(uptime)
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const getStatusColor = (percentage: number) => {
    if (percentage < 50) return 'text-success-600'
    if (percentage < 80) return 'text-warning-600'
    return 'text-error-600'
  }

  const getStatusBgColor = (percentage: number) => {
    if (percentage < 50) return 'bg-success-50'
    if (percentage < 80) return 'bg-warning-50'
    return 'bg-error-50'
  }

  if (!hasRole('admin')) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
        <p className="text-gray-600">You don't have permission to access this page.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading system information...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 text-center">
        <AlertCircle className="h-12 w-12 text-error-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Error</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchSystemInfo}
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Monitor className="h-6 w-6 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">System Information</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="autoRefresh" className="text-sm text-gray-700">
                Auto-refresh (5s)
              </label>
            </div>
            <button
              onClick={fetchSystemInfo}
              className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {systemInfo && (
        <>
          {/* System Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Uptime</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatUptime(systemInfo.uptime)}
                  </p>
                </div>
                <div className="p-3 bg-primary-50 rounded-full">
                  <Clock className="h-6 w-6 text-primary-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                  <p className={`text-2xl font-bold ${getStatusColor(systemInfo.cpu_usage)}`}>
                    {systemInfo.cpu_usage.toFixed(1)}%
                  </p>
                </div>
                <div className={`p-3 rounded-full ${getStatusBgColor(systemInfo.cpu_usage)}`}>
                  <Cpu className={`h-6 w-6 ${getStatusColor(systemInfo.cpu_usage)}`} />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                  <p className={`text-2xl font-bold ${getStatusColor(systemInfo.memory_usage.percentage)}`}>
                    {systemInfo.memory_usage.percentage.toFixed(1)}%
                  </p>
                </div>
                <div className={`p-3 rounded-full ${getStatusBgColor(systemInfo.memory_usage.percentage)}`}>
                  <MemoryStick className={`h-6 w-6 ${getStatusColor(systemInfo.memory_usage.percentage)}`} />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Processes</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {systemInfo.processes}
                  </p>
                </div>
                <div className="p-3 bg-secondary-50 rounded-full">
                  <CheckCircle className="h-6 w-6 text-secondary-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Memory Details */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Usage</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.memory_usage.total)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Used</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.memory_usage.used)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Free</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.memory_usage.free)}</span>
                </div>
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Usage</span>
                    <span>{systemInfo.memory_usage.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        systemInfo.memory_usage.percentage < 50 ? 'bg-success-600' :
                        systemInfo.memory_usage.percentage < 80 ? 'bg-warning-600' : 'bg-error-600'
                      }`}
                      style={{ width: `${systemInfo.memory_usage.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Disk Usage */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Disk Usage</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.disk_usage.total)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Used</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.disk_usage.used)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Free</span>
                  <span className="text-sm font-medium">{formatBytes(systemInfo.disk_usage.free)}</span>
                </div>
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Usage</span>
                    <span>{systemInfo.disk_usage.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        systemInfo.disk_usage.percentage < 50 ? 'bg-success-600' :
                        systemInfo.disk_usage.percentage < 80 ? 'bg-warning-600' : 'bg-error-600'
                      }`}
                      style={{ width: `${systemInfo.disk_usage.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-gray-600">Platform</p>
                <p className="text-lg font-medium text-gray-900">{systemInfo.platform}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Hostname</p>
                <p className="text-lg font-medium text-gray-900">{systemInfo.hostname}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Load Average (1m)</p>
                <p className="text-lg font-medium text-gray-900">{systemInfo.load_average[0]?.toFixed(2) || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Updated</p>
                <p className="text-lg font-medium text-gray-900">
                  {new Date(systemInfo.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default SystemInfoPage