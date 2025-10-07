import { useCallback, useEffect, useState } from 'react'
import type { DashboardState } from '../types'
import { fetchDashboard, loadSampleData } from '../api/client'

export function useDashboard() {
  const [state, setState] = useState<DashboardState>({ loading: true })

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: undefined }))
    try {
      const data = await fetchDashboard()
      setState({ data, loading: false })
    } catch (error: unknown) {
      type HttpError = { response?: { status?: number } }
      const status = typeof error === 'object' && error !== null && 'response' in error ? (error as HttpError).response?.status : undefined
      if (status === 404) {
        setState({ data: undefined, loading: false })
      } else {
        console.error('Dashboard fetch failed', error)
        setState((prev) => ({
          data: prev.data,
          loading: false,
          error: 'Failed to load dashboard.',
        }))
      }
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const loadSamples = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: undefined }))
    try {
      await loadSampleData()
      await refresh()
    } catch (error) {
      console.error('Sample data load failed', error)
      setState({ loading: false, error: 'Failed to load sample data.' })
    }
  }, [refresh])

  return { ...state, refresh, loadSamples }
}
