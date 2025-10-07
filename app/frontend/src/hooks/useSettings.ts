import { useCallback, useEffect, useState } from 'react'
import { fetchSettingsState, updateSafeMode } from '../api/client'
import type { SettingsState } from '../types'

export function useSettings() {
  const [settings, setSettings] = useState<SettingsState>({
    safe_mode: true,
    adapter_mode: 'mock',
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

  return { settings, loading, toggleSafeMode }
}
