import { useMemo, useState } from 'react'
import type { AdapterStatus } from '../types'

type AdapterKey = 'jira' | 'slack' | 'servicenow'

interface AdaptersPanelProps {
  adapters?: AdapterStatus[]
  adapterModes?: Record<AdapterKey, 'mock' | 'live'>
  safeMode: boolean
  onModeChange: (adapter: AdapterKey, mode: 'mock' | 'live') => Promise<void> | void
  onSanityCheck: (adapter: AdapterKey) => Promise<AdapterStatus>
}

const STATUS_LABELS: Record<AdapterStatus['status'], string> = {
  ok: 'Connection OK',
  error: 'Check failed',
  mock: 'Mock mode',
  unconfigured: 'Credentials needed',
  pending: 'Not checked yet',
}

const FALLBACK_ADAPTERS: AdapterStatus[] = [
  {
    key: 'jira',
    name: 'Jira backlog',
    mode: 'mock',
    safe_mode_blocked: true,
    live_configured: false,
    status: 'mock',
    detail: 'Mock backlog active. Provide Jira credentials to enable live mode.',
    last_checked: null,
  },
  {
    key: 'slack',
    name: 'Slack status broadcast',
    mode: 'mock',
    safe_mode_blocked: true,
    live_configured: false,
    status: 'mock',
    detail: 'Mock Slack adapter. Add token & channel to post updates.',
    last_checked: null,
  },
  {
    key: 'servicenow',
    name: 'ServiceNow risk table',
    mode: 'mock',
    safe_mode_blocked: true,
    live_configured: false,
    status: 'mock',
    detail: 'Mock ServiceNow data. Provide instance/user/password to sync risks.',
    last_checked: null,
  },
]

export function AdaptersPanel({ adapters, adapterModes, safeMode, onModeChange, onSanityCheck }: AdaptersPanelProps) {
  const [checking, setChecking] = useState<Record<AdapterKey, boolean>>({} as Record<AdapterKey, boolean>)

  const mergedAdapters = useMemo(() => {
    if (adapters && adapters.length > 0) {
      return adapters
    }
    if (adapterModes) {
      return FALLBACK_ADAPTERS.map((adapter) => ({
        ...adapter,
        mode: adapterModes[adapter.key],
        safe_mode_blocked: safeMode,
      }))
    }
    return FALLBACK_ADAPTERS.map((adapter) => ({ ...adapter, safe_mode_blocked: safeMode }))
  }, [adapters, adapterModes, safeMode])

  const handleModeChange = async (key: AdapterKey, mode: 'mock' | 'live') => {
    try {
      await onModeChange(key, mode)
    } catch {
      // notification handled upstream
    }
  }

  const handleSanityCheck = async (key: AdapterKey) => {
    setChecking((prev) => ({ ...prev, [key]: true }))
    let result: AdapterStatus | undefined
    try {
      result = await onSanityCheck(key)
    } catch {
      // notification handled upstream
    } finally {
      setChecking((prev) => ({ ...prev, [key]: false }))
    }
    return result
  }

  return (
    <section className="section-card adapters-card" aria-labelledby="adapters-heading">
      <div className="card-heading">
        <h3 id="adapters-heading">Adapters</h3>
      </div>
      <p className="adapters-copy">
        Toggle mock/live adapters and run sanity checks. Safe Mode keeps everything local until you opt in.
      </p>
      <div className="adapters-grid">
        {mergedAdapters.map((adapter) => {
          const isLive = adapter.mode === 'live'
          const liveDisabled = safeMode || adapter.safe_mode_blocked || !adapter.live_configured
          const isChecking = checking[adapter.key]
          const lastCheckedLabel = adapter.last_checked
            ? new Date(adapter.last_checked).toLocaleString()
            : 'Not checked yet'
          return (
            <article key={adapter.key} className={`adapter-card status-${adapter.status}`}>
              <header className="adapter-header">
                <h4>{adapter.name}</h4>
                <span className="adapter-status-label">{STATUS_LABELS[adapter.status]}</span>
              </header>
              <p>{adapter.detail}</p>
              <div className="adapter-controls">
                <div className="mode-toggle" role="group" aria-label={`Adapter mode for ${adapter.name}`}>
                  <button
                    type="button"
                    className={`toggle-pill ${!isLive ? 'active' : ''}`}
                    onClick={() => handleModeChange(adapter.key, 'mock')}
                    disabled={adapter.mode === 'mock'}
                  >
                    Mock
                  </button>
                  <button
                    type="button"
                    className={`toggle-pill ${isLive ? 'active' : ''}`}
                    onClick={() => handleModeChange(adapter.key, 'live')}
                    disabled={liveDisabled || adapter.mode === 'live'}
                    title={liveDisabled ? 'Provide credentials and disable Safe Mode to enable live mode.' : 'Enable read-only live adapter.'}
                  >
                    Live
                  </button>
                </div>
                <button
                  className="button ghost"
                  type="button"
                  onClick={() => handleSanityCheck(adapter.key)}
                  disabled={safeMode || adapter.mode !== 'live' || isChecking || !adapter.live_configured}
                >
                  {isChecking ? 'Checking…' : 'Sanity check'}
                </button>
              </div>
              <span className="adapter-timestamp">Last check: {lastCheckedLabel}</span>
            </article>
          )
        })}
      </div>
    </section>
  )
}
