import { useCallback, useEffect, useState } from 'react'
import { fetchSettingsState, runAdapterCheck, updateAdapterMode, updateSafeMode } from '../api/client'
import type { AdapterStatus, SettingsState } from '../types'

export function useSettings() {
  const [settings, setSettings] = useState<SettingsState>({
    safe_mode: true,
    adapter_mode: 'mock',
    adapter_modes: {
      jira: 'mock',
      slack: 'mock',
      servicenow: 'mock',
    },
    adapters: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchSettingsState()
        setSettings(data)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const toggleSafeMode = useCallback(
    async (value: boolean) => {
      const data = await updateSafeMode(value)
      setSettings((prev) => ({ ...prev, ...data }))
    },
    [],
  )

  const setAdapterMode = useCallback(
    async (adapter: 'jira' | 'slack' | 'servicenow', mode: 'mock' | 'live') => {
      const data = await updateAdapterMode(adapter, mode)
      setSettings((prev) => ({
        ...prev,
        adapter_mode: data.adapter_mode,
        adapter_modes: data.adapter_modes ?? prev.adapter_modes,
        adapters: data.adapters ?? prev.adapters,
      }))
    },
    [],
  )

  const sanityCheck = useCallback(
    async (adapter: 'jira' | 'slack' | 'servicenow'): Promise<AdapterStatus> => {
      const result = await runAdapterCheck(adapter)
      setSettings((prev) => {
        const current = prev.adapters ?? []
        const next = current.some((item) => item.key === result.key)
          ? current.map((item) => (item.key === result.key ? result : item))
          : [...current, result]
        return { ...prev, adapters: next }
      })
      return result
    },
    [],
  )

  return { settings, loading, toggleSafeMode, setAdapterMode, sanityCheck }
}
