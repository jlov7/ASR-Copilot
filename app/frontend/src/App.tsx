import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'
import './index.css'
import { TourModal } from './components/TourModal'
import { DashboardView } from './components/DashboardView'
import { useDashboard } from './hooks/useDashboard'
import { useSettings } from './hooks/useSettings'
import { exportStatusPack, updateRoi, uploadDataset } from './api/client'
import type { RoiUpdateRequest } from './types'

const ONBOARDING_KEY = 'asr_onboarding_complete'
const CHECKLIST_KEY = 'asr_onboarding_checklist'

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

export default function App() {
  const { data, loading, error, refresh, loadSamples } = useDashboard()
  const { settings, loading: settingsLoading, toggleSafeMode } = useSettings()
  const [tourOpen, setTourOpen] = useState<boolean>(() => localStorage.getItem(ONBOARDING_KEY) !== 'done')
  const [tourStep, setTourStep] = useState(0)
  const [toast, setToast] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)
  const [roiSaving, setRoiSaving] = useState(false)
  const [checklist, setChecklist] = useState<ChecklistState>(() => loadChecklist())
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    saveChecklist(checklist)
  }, [checklist])

  const modeLabel = settings.safe_mode ? 'Safe Mode • mock adapters' : 'Live Mode • read-only adapters'

  const heroSubtitle = useMemo(() => {
    if (!data) {
      return `${modeLabel} | Upload your backlog, risks, and notes—ASR Copilot delivers executive clarity in minutes.`
    }
    return `Dataset updated ${new Date(data.meta.last_updated).toLocaleString()} • Hash ${data.meta.dataset_hash.slice(0, 8)} • ${modeLabel}`
  }, [data, modeLabel])

  const showToast = useCallback((message: string) => {
    setToast(message)
    setTimeout(() => setToast(null), 4000)
  }, [])

  const markChecklist = (key: string) => {
    setChecklist((prev) => ({ ...prev, [key]: true }))
  }

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

  const handleExport = async () => {
    if (!data) return
    try {
      setExporting(true)
      const result = await exportStatusPack({ include_markdown: true, include_png: true })
      showToast(`Status Pack saved to ${result.markdown_path ?? 'out/'}.`)
      markChecklist('export')
    } catch (exportError) {
      showToast('Export failed – check console logs for details.')
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
      showToast('ROI assumptions updated.')
      markChecklist('roi')
    } catch (roiError) {
      showToast('Unable to save ROI assumptions.')
      console.error(roiError)
    } finally {
      setRoiSaving(false)
    }
  }

  const handleSampleLoad = async () => {
    await loadSamples()
    showToast('Sample program loaded. Dashboard ready.')
    markChecklist('upload')
  }

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = event.currentTarget
    const formData = new FormData(form)
    const requiredFields = ['tasks', 'risks', 'status_notes', 'evm_baseline']
    const missing = requiredFields.filter((field) => !formData.get(field))
    if (missing.length > 0) {
      showToast(`Missing files: ${missing.join(', ')}`)
      return
    }
    try {
      setUploading(true)
      await uploadDataset(formData)
      await refresh()
      showToast('Dataset uploaded successfully.')
      markChecklist('upload')
      form.reset()
    } catch (uploadError) {
      showToast('Upload failed – validate your CSV/MD format.')
      console.error(uploadError)
    } finally {
      setUploading(false)
    }
  }

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
        <div className="toast" role="status">
          {toast}
        </div>
      )}

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
          <button className="button secondary" onClick={handleReplayTour}>
            Replay onboarding tour
          </button>
          <button className="button primary" onClick={handleExport} disabled={exporting || !data}>
            {exporting ? 'Exporting…' : 'Export Status Pack'}
          </button>
        </div>
      </header>
      {!settingsLoading && (
        <div className={`safety-banner ${settings.safe_mode ? 'safe' : 'live'}`} role="status" aria-live="polite">
          {settings.safe_mode ? 'SAFE MODE • Mock adapters only. Provide credentials to enable live integrations.' : 'LIVE MODE • Read-only adapters active. Tokens are redacted in logs.'}
        </div>
      )}

      <section className="hero">
        <div>
          <h2>Automate your status rituals.</h2>
          <p className="hero-copy">{heroSubtitle}</p>
          <div className="cta-group">
            <button className="button primary" onClick={() => setTourOpen(true)}>
              Start guided tour
            </button>
            <button className="button secondary" onClick={handleSampleLoad}>
              Try with sample data
            </button>
          </div>
        </div>
        <div className="checklist" aria-label="Onboarding checklist">
          <h3>First-time checklist</h3>
          {checklistEntries}
        </div>
      </section>

      <section className="upload-panel" aria-labelledby="upload-heading">
        <h3 id="upload-heading">Upload your data</h3>
        <p>We only store data locally. Provide CSVs/Markdown matching the schema in the README, or load the sample dataset.</p>
        <form onSubmit={handleUpload} className="upload-grid">
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
            <button className="button primary" type="submit" disabled={uploading}>
              {uploading ? 'Uploading…' : 'Process files'}
            </button>
          </div>
        </form>
      </section>

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
    </div>
  )
}
