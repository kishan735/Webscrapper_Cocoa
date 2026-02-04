import { useState, useEffect, useCallback } from 'react'

export function useApi(apiFunction, dependencies = [], options = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const { autoFetch = true, initialData = null } = options

  const fetchData = useCallback(async (...args) => {
    setLoading(true)
    setError(null)

    try {
      const result = await apiFunction(...args)
      setData(result)
      return result
    } catch (err) {
      setError(err.message || 'An error occurred')
      setData(initialData)
      return null
    } finally {
      setLoading(false)
    }
  }, [apiFunction])

  useEffect(() => {
    if (autoFetch) {
      fetchData()
    } else {
      setLoading(false)
    }
  }, dependencies)

  return { data, loading, error, refetch: fetchData }
}

export function usePollingApi(apiFunction, interval = 60000, dependencies = []) {
  const { data, loading, error, refetch } = useApi(apiFunction, dependencies)

  useEffect(() => {
    const pollInterval = setInterval(() => {
      refetch()
    }, interval)

    return () => clearInterval(pollInterval)
  }, [interval, refetch])

  return { data, loading, error, refetch }
}

export default useApi
