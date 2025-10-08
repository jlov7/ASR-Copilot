import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import './App.css'
import './index.css'
import { TourModal } from './components/TourModal'
import { DashboardView } from './components/DashboardView'
import { AdaptersPanel } from './components/AdaptersPanel'
import { ShortcutsModal } from './components/ShortcutsModal'
import { EmptyStateTiles } from './components/EmptyStateTiles'
import { useDashboard } from './hooks/useDashboard'
import { useSettings } from './hooks/useSettings'
import {
  exportStatusPack,
  fetchExportMarkdown,
  purgeLocalData,
  revealExportPath,
  runAutomationDryRun,
  updateRoi,
  uploadDataset,
} from './api/client'
import type { RoiUpdateRequest } from './types'
import { ToastBar } from './components/ToastBar'
import { GuidedMode, type GuidedScenario } from './features/landing/GuidedMode'
import { WelcomeModal } from './components/WelcomeModal'
import { PrivacyPanel } from './components/PrivacyPanel'

const ONBOARDING_KEY = 'asr_onboarding_complete'
const CHECKLIST_KEY = 'asr_onboarding_checklist'
const WELCOME_KEY = 'asr_welcome_seen'

const CHECKLIST_ITEMS = [
  { key: 'upload', label: 'Upload your backlog, risk register, and status notes.' },
  { key: 'roi', label: 'Review the ROI assumptions.' },
  { key: 'export', label: 'Export a Status Pack.' },
  { key: 'tour', label: 'Complete the onboarding tour.' },
]

type ChecklistState = Record<string, boolean>

function loadChecklist(): ChecklistState {
  const raw = localStorage.getItem(CHECKLIST_KEY)
  if (raw) {
    try {
      return JSON.parse(raw)
    } catch (parsingError) {
      console.error('Failed to parse checklist cache', parsingError)
      return {}
    }
  }
  return {}
}

function saveChecklist(state: ChecklistState) {
  localStorage.setItem(CHECKLIST_KEY, JSON.stringify(state))
}

type ToastTone = 'info' | 'success' | 'error'

interface ToastAction {
  label: string
  onClick: () => void | Promise<void>
}

interface ToastConfig {
  message: string
  detail?: ReactNode
  tone?: ToastTone
  actions?: ToastAction[]
  durationMs?: number | null
  path?: string
  onCopyPath?: (path: string) => void | Promise<void>
}

type ToastInput = string | ToastConfig

const SAFE_MODE_DOC_URL =
  'https://github.com/jlov7/ASR-Copilot?tab=readme-ov-file#environment-configuration'

type AdapterKey = 'jira' | 'slack' | 'servicenow'

const ADAPTER_LABELS: Record<AdapterKey, string> = {
  jira: 'Jira',
  slack: 'Slack',
  servicenow: 'ServiceNow',
}

export default function App() {
  const { data, loading, error, refresh, loadSamples } = useDashboard()
  const { settings, loading: settingsLoading, toggleSafeMode, setAdapterMode, sanityCheck } = useSettings()
  const [tourOpen, setTourOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') {
      return false
    }
    return localStorage.getItem(ONBOARDING_KEY) !== 'done'
  })
  const [tourStep, setTourStep] = useState(0)
  const toastTimer = useRef<number | null>(null)
  const [toast, setToast] = useState<ToastConfig | null>(null)
  const [exporting, setExporting] = useState(false)
  const [roiSaving, setRoiSaving] = useState(false)
  const [checklist, setChecklist] = useState<ChecklistState>(() => loadChecklist())
  const [uploading, setUploading] = useState(false)
  const [dryRunning, setDryRunning] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [welcomeOpen, setWelcomeOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') {
      return false
    }
    return localStorage.getItem(WELCOME_KEY) !== 'done'
  })
  const [guidedLoading, setGuidedLoading] = useState(false)
  const [sampleLoading, setSampleLoading] = useState(false)
  const [purging, setPurging] = useState(false)
  const [impactSummary, setImpactSummary] = useState<{ minutes: number } | null>(null)
  const guidedSectionRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    saveChecklist(checklist)
  }, [checklist])

  useEffect(() => {
    setImpactSummary(null)
  }, [data?.meta.dataset_hash])

  useEffect(() => {
    return () => {
      if (toastTimer.current !== null) {
        window.clearTimeout(toastTimer.current)
      }
    }
  }, [])

  const modeLabel = settings.safe_mode ? 'Safe Mode • mock adapters' : 'Live Mode • read-only adapters'

  const heroSubtitle = useMemo(() => {
    if (!data) {
      return `${modeLabel} | Upload your backlog, risks, and notes—ASR Copilot delivers executive clarity in minutes.`
    }
    return `Dataset updated ${new Date(data.meta.last_updated).toLocaleString()} • Hash ${data.meta.dataset_hash.slice(0, 8)} • ${modeLabel}`
  }, [data, modeLabel])

  const showEmptyTiles = !loading && !data
  const showToast = useCallback((input: ToastInput) => {
    if (toastTimer.current !== null) {
      window.clearTimeout(toastTimer.current)
      toastTimer.current = null
    }
    const config: ToastConfig = typeof input === 'string' ? { message: input } : input
    const duration = config.durationMs === undefined ? 5000 : config.durationMs
    setToast(config)
    if (duration !== null) {
      toastTimer.current = window.setTimeout(() => {
        setToast(null)
        toastTimer.current = null
      }, duration)
    }
  }, [])

  const dismissToast = useCallback(() => {
    if (toastTimer.current !== null) {
      window.clearTimeout(toastTimer.current)
      toastTimer.current = null
    }
    setToast(null)
  }, [])

  const markChecklist = useCallback((key: string) => {
    setChecklist((prev) => ({ ...prev, [key]: true }))
  }, [])

  const acknowledgeWelcome = useCallback(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(WELCOME_KEY, 'done')
    }
    setWelcomeOpen(false)
  }, [])

  const focusUploadForm = useCallback(() => {
    const target = document.getElementById('dataset-upload-form')
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    const input = document.querySelector<HTMLInputElement>('#dataset-upload-form input[name="tasks"]')
    input?.focus()
  }, [])

  const focusGuidedMode = useCallback(() => {
    const target = guidedSectionRef.current
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      target.focus({ preventScroll: true })
    }
  }, [])

  const handleTourNext = () => {
    if (tourStep === 4) {
      localStorage.setItem(ONBOARDING_KEY, 'done')
      setTourOpen(false)
      markChecklist('tour')
    } else {
      setTourStep((prev) => Math.min(prev + 1, 4))
    }
  }

  const handleTourPrev = () => {
    setTourStep((prev) => Math.max(prev - 1, 0))
  }

  const handleReplayTour = () => {
    setTourStep(0)
    setTourOpen(true)
    localStorage.removeItem(ONBOARDING_KEY)
  }

  const handleRevealExportPath = useCallback(
    async (path: string) => {
      try {
        await revealExportPath(path)
      } catch (revealError) {
        console.error('Reveal export failed', revealError)
        dismissToast()
        showToast({
          message: 'Unable to reveal export location. Open the file from the out/ directory.',
          tone: 'error',
          durationMs: 6000,
        })
      }
    },
    [dismissToast, showToast],
  )

  const handleCopyExportMarkdown = useCallback(
    async (path: string) => {
      try {
        const content = await fetchExportMarkdown(path)
        await navigator.clipboard.writeText(content)
        dismissToast()
        showToast({
          message: 'Status Pack Markdown copied to clipboard.',
          tone: 'success',
        })
      } catch (copyError) {
        console.error('Copy Markdown failed', copyError)
        dismissToast()
        showToast({
          message: 'Copy failed – open the Markdown file from the out/ folder.',
          tone: 'error',
          durationMs: 6000,
        })
      }
    },
    [dismissToast, showToast],
  )

  const handleWelcomeGuided = useCallback(() => {
    acknowledgeWelcome()
    focusGuidedMode()
  }, [acknowledgeWelcome, focusGuidedMode])

  const handleWelcomeUpload = useCallback(() => {
    acknowledgeWelcome()
    focusUploadForm()
  }, [acknowledgeWelcome, focusUploadForm])

  const handleWelcomeLearnMore = useCallback(() => {
    acknowledgeWelcome()
    if (typeof window !== 'undefined') {
      window.open('https://github.com/jlov7/ASR-Copilot/blob/main/WHY.md', '_blank', 'noopener')
    }
  }, [acknowledgeWelcome])

  const handleExport = async () => {
    if (!data) return
    try {
      setExporting(true)
      const result = await exportStatusPack({ include_markdown: true, include_png: true })
      const markdownPath = result.markdown_path ?? undefined
      const displayPath = markdownPath ?? result.chart_paths[0] ?? null
      const detail = 'Use the quick actions below to open the export or copy it for sharing.'
      const actions: ToastAction[] = []
      if (displayPath) {
        actions.push({
          label: 'Reveal in Finder/Explorer',
          onClick: () => handleRevealExportPath(displayPath),
        })
      }
      if (markdownPath) {
        actions.push({
          label: 'Copy Markdown',
          onClick: () => handleCopyExportMarkdown(markdownPath),
        })
      }
      showToast({
        message: 'Status Pack saved locally.',
        detail,
        tone: 'success',
        actions,
        durationMs: null,
        path: displayPath ?? undefined,
      })
      if (data?.roi) {
        const timeMultiplier = data.roi.modifiers?.time_saved_multiplier ?? 1
        const minutesRaw = data.roi.assumptions.reduce((total, assumption) => {
          const hoursPerOccurrence = assumption.hours_saved * timeMultiplier
          return total + hoursPerOccurrence * 60 * assumption.team_size
        }, 0)
        const roundedMinutes = minutesRaw > 0 ? Math.max(5, Math.round(minutesRaw / 5) * 5) : 45
        setImpactSummary({ minutes: roundedMinutes })
      }
      markChecklist('export')
    } catch (exportError) {
      showToast({
        message: 'Export failed – check console logs for details.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error(exportError)
    } finally {
      setExporting(false)
    }
  }

  const handleSaveRoi = async (payload: RoiUpdateRequest) => {
    try {
      setRoiSaving(true)
      await updateRoi(payload)
      await refresh()
      showToast({
        message: 'ROI assumptions updated.',
        tone: 'success',
      })
      markChecklist('roi')
    } catch (roiError) {
      showToast({
        message: 'Unable to save ROI assumptions.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error(roiError)
    } finally {
      setRoiSaving(false)
    }
  }

  const handleSampleLoad = useCallback(async () => {
    if (sampleLoading) {
      return
    }
    acknowledgeWelcome()
    setSampleLoading(true)
    try {
      await loadSamples()
      showToast({
        message: 'Sample program loaded. Dashboard ready.',
        tone: 'success',
      })
      markChecklist('upload')
      setImpactSummary(null)
    } catch (sampleError) {
      showToast({
        message: 'Unable to load sample data. Check logs for details.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error('Sample load failed', sampleError)
    } finally {
      setSampleLoading(false)
    }
  }, [acknowledgeWelcome, loadSamples, markChecklist, sampleLoading, showToast])

  const handleGuidedScenarioLaunch = useCallback(
    async (scenario: GuidedScenario) => {
      acknowledgeWelcome()
      setGuidedLoading(true)
      try {
        await loadSamples({ scenario: scenario.id, seed: scenario.seed })
        showToast({
          message: `${scenario.title} scenario loaded. Dashboard ready.`,
          tone: 'success',
        })
        markChecklist('upload')
        setImpactSummary(null)
      } catch (error) {
        console.error('Guided scenario load failed', error)
        showToast({
          message: 'Unable to load guided scenario. Check logs for details.',
          tone: 'error',
          durationMs: 6000,
        })
      } finally {
        setGuidedLoading(false)
      }
    },
    [acknowledgeWelcome, loadSamples, markChecklist, showToast],
  )

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = event.currentTarget
    const formData = new FormData(form)
    const requiredFields = ['tasks', 'risks', 'status_notes', 'evm_baseline']
    const missing = requiredFields.filter((field) => !formData.get(field))
    if (missing.length > 0) {
      showToast({
        message: `Missing files: ${missing.join(', ')}`,
        tone: 'error',
        durationMs: 6000,
      })
      return
    }
    try {
      setUploading(true)
      await uploadDataset(formData)
      await refresh()
      showToast({
        message: 'Dataset uploaded successfully.',
        tone: 'success',
      })
      markChecklist('upload')
      setImpactSummary(null)
      form.reset()
    } catch (uploadError) {
      showToast({
        message: 'Upload failed – validate your CSV/MD format.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error(uploadError)
    } finally {
      setUploading(false)
    }
  }

  const handleAdapterModeChange = useCallback(
    async (adapter: AdapterKey, mode: 'mock' | 'live') => {
      try {
        await setAdapterMode(adapter, mode)
        showToast({
          message: `${ADAPTER_LABELS[adapter]} set to ${mode === 'live' ? 'live' : 'mock'} mode.`,
          tone: 'success',
        })
      } catch (error) {
        showToast({
          message: 'Unable to update adapter mode. Check console for details.',
          tone: 'error',
          durationMs: 6000,
        })
        console.error('Adapter mode update failed', error)
      }
    },
    [setAdapterMode, showToast],
  )

  const handleAdapterCheck = useCallback(
    async (adapter: AdapterKey) => {
      try {
        const result = await sanityCheck(adapter)
        const success = result.status === 'ok'
        showToast({
          message: `${result.name} ${success ? 'check passed.' : 'check completed with issues.'}`,
          tone: success ? 'success' : 'error',
          durationMs: 6000,
        })
        return result
      } catch (error) {
        showToast({
          message: 'Adapter check failed. Verify credentials and try again.',
          tone: 'error',
          durationMs: 6000,
        })
        console.error('Adapter check failed', error)
        throw error
      }
    },
    [sanityCheck, showToast],
  )

  const handlePurgeLocalData = useCallback(async () => {
    try {
      setPurging(true)
      await purgeLocalData()
      await refresh()
      showToast({
        message: 'Local data purged. Dashboard reset.',
        tone: 'success',
      })
      setImpactSummary(null)
    } catch (purgeError) {
      showToast({
        message: 'Unable to purge local data. Check logs for details.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error('Purge local data failed', purgeError)
    } finally {
      setPurging(false)
    }
  }, [refresh, showToast])

  const handleDryRun = useCallback(async () => {
    try {
      setDryRunning(true)
      await runAutomationDryRun()
      await refresh()
      showToast({
        message: 'Dry-run completed. Automation loop updated.',
        tone: 'success',
      })
    } catch (error) {
      showToast({
        message: 'Dry-run failed – check console for details.',
        tone: 'error',
        durationMs: 6000,
      })
      console.error('Dry run failed', error)
    } finally {
      setDryRunning(false)
    }
  }, [refresh, showToast])

  const shortcuts = useMemo(
    () => [
      { key: 'Shift + ?', description: 'Toggle this shortcuts panel' },
      { key: 't', description: 'Start guided tour' },
      { key: 'l', description: 'Load sample program' },
      { key: 'u', description: 'Scroll to upload form' },
      { key: 'e', description: 'Export Status Pack' },
      { key: 'd', description: 'Run automation dry-run' },
    ],
    [],
  )

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
        return
      }
      if (event.key === 'Escape' && shortcutsOpen) {
        setShortcutsOpen(false)
        event.preventDefault()
        return
      }
      if ((event.shiftKey && event.key === '?') || (event.key === '/' && event.shiftKey)) {
        setShortcutsOpen((prev) => !prev)
        event.preventDefault()
        return
      }
      if (event.metaKey || event.ctrlKey || event.altKey) {
        return
      }
      const key = event.key.toLowerCase()
      if (key === 't') {
        setTourStep(0)
        setTourOpen(true)
        event.preventDefault()
      } else if (key === 'l') {
        void handleSampleLoad()
        event.preventDefault()
      } else if (key === 'u') {
        focusUploadForm()
        event.preventDefault()
      } else if (key === 'e') {
        if (data) {
          void handleExport()
        } else {
          showToast({ message: 'Load data before exporting.', tone: 'info' })
        }
        event.preventDefault()
      } else if (key === 'd') {
        void handleDryRun()
        event.preventDefault()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [data, focusUploadForm, handleDryRun, handleExport, handleSampleLoad, shortcutsOpen, showToast])

  const checklistEntries = CHECKLIST_ITEMS.map((item) => (
    <label key={item.key} className="checklist-item">
      <input
        type="checkbox"
        checked={Boolean(checklist[item.key])}
        onChange={(event) => setChecklist((prev) => ({ ...prev, [item.key]: event.target.checked }))}
      />
      <span>{item.label}</span>
    </label>
  ))

  return (
    <div className="app-shell">
      {toast && (
        <ToastBar
          message={toast.message}
          detail={toast.detail}
          tone={toast.tone}
          actions={toast.actions}
          path={toast.path}
          onCopyPath={toast.onCopyPath}
          onClose={dismissToast}
        />
      )}

      <WelcomeModal
        open={welcomeOpen}
        onClose={acknowledgeWelcome}
        onGuided={handleWelcomeGuided}
        onUpload={handleWelcomeUpload}
        onLearnMore={handleWelcomeLearnMore}
      />

      <header className="top-nav">
        <div className="brand">
          <h1>ASR Copilot</h1>
          <span className="tagline">Autonomy–Status–Risk copiloting for TMT/Telco programs</span>
        </div>
        <div className="nav-actions">
          <div className="safe-toggle" aria-live="polite">
            <label htmlFor="safe-mode-toggle">Safe Mode</label>
            <input
              id="safe-mode-toggle"
              type="checkbox"
              checked={settings.safe_mode}
              disabled={settingsLoading}
              onChange={(event) => toggleSafeMode(event.target.checked)}
            />
          </div>
          <button
            className="button secondary"
            onClick={() => {
              void handleSampleLoad()
            }}
            disabled={sampleLoading}
            title="Reload the bundled sample data and reset the dashboard state."
          >
            {sampleLoading ? 'Loading sample…' : 'Reset to sample data'}
          </button>
          <button
            className="button link"
            onClick={handleReplayTour}
            title="Restart the five-step onboarding overlays at any time."
          >
            Replay tour
          </button>
          <button
            className="button primary"
            onClick={handleExport}
            disabled={exporting || !data}
            title="Generate Markdown and charts, then surface reveal/copy actions."
          >
            {exporting ? 'Exporting…' : 'Export Status Pack'}
          </button>
        </div>
      </header>
      {!settingsLoading && (
        <div className={`safety-banner ${settings.safe_mode ? 'safe' : 'live'}`} role="status" aria-live="polite">
          {settings.safe_mode ? (
            <>
              Safe Mode: <strong>ON</strong> – outbound calls disabled.{' '}
              <a href={SAFE_MODE_DOC_URL} target="_blank" rel="noreferrer">
                What's this?
              </a>
            </>
          ) : (
            <>
              Safe Mode: <strong>OFF</strong> – read-only adapters may call live APIs.{' '}
              <a href={SAFE_MODE_DOC_URL} target="_blank" rel="noreferrer">
                What's this?
              </a>
            </>
          )}
        </div>
      )}

      {impactSummary && (
        <div className="impact-ribbon" role="status" aria-live="polite">
          <div>
            <p className="impact-title">What problem did we just solve?</p>
            <p className="impact-body">
              Saved ~{impactSummary.minutes} minutes by auto-assembling the status pack and surfacing top risks.
            </p>
            <p className="impact-body">Tune the ROI panel to match your cadence and rates.</p>
          </div>
          <button
            className="button ghost"
            type="button"
            onClick={() => setImpactSummary(null)}
            aria-label="Dismiss export impact summary"
          >
            ✕
          </button>
        </div>
      )}

      {showEmptyTiles && (
        <EmptyStateTiles
          onShowGuided={focusGuidedMode}
          onLoadSample={handleSampleLoad}
          onFocusUpload={focusUploadForm}
          safeModeDocUrl={SAFE_MODE_DOC_URL}
          sampleLoading={sampleLoading}
        />
      )}

      <section className="hero">
        <div>
          <h2>Automate your status rituals.</h2>
          <p className="hero-lede">
            <strong>See it in 15 seconds</strong> → Click <span className="hero-highlight">Instant Demo</span> below (no files needed).
          </p>
          <p className="hero-copy">
            ASR Copilot turns weekly status drudgery into a 3-minute executive update: <em>health (RAG)</em> → <em>EVM (CPI/SPI)</em> →{' '}
            <em>Top risks</em> → <em>What changed</em> → <em>1-click export</em>.
          </p>
          <p className="hero-safety">
            <strong>No integrations.</strong> Safe Mode by default. Deterministic analytics.
          </p>
          <p className="hero-meta">{heroSubtitle}</p>
          <div className="cta-group">
            <button
              className="button primary"
              onClick={handleWelcomeGuided}
              title="Scroll to the Instant Demo tiles and launch a scenario instantly."
            >
              Launch Instant Demo
            </button>
            <button className="button secondary" onClick={handleWelcomeUpload} title="Jump to the upload form and process your own artifacts.">
              Process your files
            </button>
            <button
              className="button ghost"
              onClick={() => {
                acknowledgeWelcome()
                handleReplayTour()
              }}
              title="Walk through the five-step onboarding overlays."
            >
              Start guided tour
            </button>
          </div>
        </div>
        <div className="checklist" aria-label="Onboarding checklist">
          <h3>First-time checklist</h3>
          {checklistEntries}
        </div>
      </section>

      <div ref={guidedSectionRef} className="guided-anchor" tabIndex={-1}>
        <GuidedMode busy={guidedLoading} onLaunchScenario={handleGuidedScenarioLaunch} />
      </div>

      <section className="upload-panel" aria-labelledby="upload-heading">
        <h3 id="upload-heading">Upload your data</h3>
        <p>We only store data locally. Provide CSVs/Markdown matching the schema in the README, or load the sample dataset.</p>
        <form id="dataset-upload-form" onSubmit={handleUpload} className="upload-grid">
          <label>
            Task backlog CSV
            <input required type="file" name="tasks" accept=".csv" />
          </label>
          <label>
            Risk register CSV
            <input required type="file" name="risks" accept=".csv" />
          </label>
          <label>
            Status notes Markdown
            <input required type="file" name="status_notes" accept=".md,.markdown" />
          </label>
          <label>
            EVM baseline CSV
            <input required type="file" name="evm_baseline" accept=".csv" />
          </label>
          <div className="cta-group" style={{ justifyContent: 'flex-end', marginTop: '12px' }}>
            <button
              className="button primary"
              type="submit"
              disabled={uploading}
              title="Upload backlog, risks, notes, and EVM baseline to refresh the dashboard."
            >
              {uploading ? 'Uploading…' : 'Process files'}
            </button>
          </div>
        </form>
      </section>

      {!settingsLoading && (
        <>
          <AdaptersPanel
            adapters={settings.adapters}
            adapterModes={settings.adapter_modes}
            safeMode={settings.safe_mode}
            onModeChange={handleAdapterModeChange}
            onSanityCheck={handleAdapterCheck}
          />
          <PrivacyPanel onPurge={handlePurgeLocalData} purging={purging} />
        </>
      )}

      {error && (
        <div className="error-banner" role="alert">
          <span>{error}</span>
          <button className="button ghost" onClick={refresh}>
            Retry
          </button>
        </div>
      )}

      <DashboardView
        data={data}
        isLoading={loading}
        exporting={exporting}
        onExport={handleExport}
        onSaveRoi={handleSaveRoi}
        roiSaving={roiSaving}
        onNotify={showToast}
        onDryRun={handleDryRun}
        dryRunning={dryRunning}
      />

      <footer style={{ marginTop: '48px', color: '#4a5b82', fontSize: '0.85rem' }}>
        <p>
          ASR Copilot – built for PMs navigating autonomy programs. Adapter mode:{' '}
          <strong>{settings.adapter_mode}</strong> • Safe Mode:{' '}
          <strong>{settings.safe_mode ? 'On' : 'Off'}</strong>
        </p>
      </footer>

      <TourModal
        open={tourOpen}
        stepIndex={tourStep}
        onNext={handleTourNext}
        onPrev={handleTourPrev}
        onClose={() => {
          setTourOpen(false)
          localStorage.setItem(ONBOARDING_KEY, 'done')
        }}
      />
      {shortcutsOpen && <ShortcutsModal shortcuts={shortcuts} onClose={() => setShortcutsOpen(false)} />}
    </div>
  )
}
