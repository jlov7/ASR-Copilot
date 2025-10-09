import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import type {
  DashboardPayload,
  RAGState,
  RoiAssumption,
  RoiModifiers,
  RoiPreset,
  RoiUpdateRequest,
  RiskListItem,
} from '../types'
import { EvmPrimerModal, type PrimerMetric } from './EvmPrimerModal'

interface DashboardViewProps {
  data?: DashboardPayload
  isLoading: boolean
  exporting: boolean
  onExport: () => Promise<void>
  onPreview: () => Promise<void>
  previewing: boolean
  onSaveRoi: (payload: RoiUpdateRequest) => Promise<void>
  roiSaving: boolean
  onNotify?: (message: string) => void
  onDryRun: () => Promise<void>
  dryRunning: boolean
}

function ragFromMetrics(spi: number | null, cpi: number | null): RAGState {
  if (spi === null || cpi === null) return 'Watch'
  if (spi >= 1 && cpi >= 1) return 'On Track'
  if (spi >= 0.95 && cpi >= 0.95) return 'Watch'
  return 'At Risk'
}

const changeLabel: Record<'added' | 'updated' | 'removed', string> = {
  added: 'New',
  updated: 'Updated',
  removed: 'Removed',
}

const DOCS_BASE_URL = 'https://github.com/jlov7/ASR-Copilot/blob/main'

const EXPLAIN_COPY: Record<'evm' | 'risks', { title: string; body: string; linkLabel?: string; href?: string }> = {
  evm: {
    title: 'How to read program health',
    body: 'We translate CPI (cost) and SPI (schedule) into the RAG pill. ≥1.0 stays green, 0.95 warns amber, and anything under 0.9 means escalate. All numbers come from the baseline CSV you uploaded.',
    linkLabel: 'Learn EVM basics',
    href: `${DOCS_BASE_URL}/docs/EVM-PRIMER.md`,
  },
  risks: {
    title: 'How the risk watchlist works',
    body: 'We rank the top five risks by probability × impact so you see the most urgent items first. Severity pills, owners, and due dates read like a talk track for execs.',
    linkLabel: 'See demo talking points',
    href: `${DOCS_BASE_URL}/docs/DEMOS.md`,
  },
}

type ExplainKey = keyof typeof EXPLAIN_COPY

const TRIGGER_LABELS: Record<'unknown' | 'upload' | 'dry_run' | 'seed', string> = {
  unknown: 'Manual run',
  upload: 'Dataset upload',
  dry_run: 'Dry-run',
  seed: 'Sample seed',
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value)
}

function formatHours(value: number) {
  return `${value.toFixed(0)} hrs`
}

function cloneAssumptions(assumptions: RoiAssumption[]): RoiAssumption[] {
  return assumptions.map((assumption) => ({ ...assumption }))
}

function computePreview(assumptions: RoiAssumption[], modifiers: RoiModifiers) {
  let totalAnnual = 0
  let totalHours = 0
  assumptions.forEach((assumption) => {
    const adjustedFrequency = assumption.frequency_per_month * modifiers.frequency_multiplier
    const adjustedHours = assumption.hours_saved * modifiers.time_saved_multiplier
    const annualOccurrences = adjustedFrequency * 12
    const hoursSaved = adjustedHours * annualOccurrences * assumption.team_size
    totalHours += hoursSaved
    totalAnnual += hoursSaved * assumption.pm_hourly_cost
  })
  return {
    annual: Number(totalAnnual.toFixed(2)),
    monthly: Number((totalAnnual / 12).toFixed(2)),
    hours: Number(totalHours.toFixed(2)),
  }
}

export function DashboardView({
  data,
  isLoading,
  exporting,
  onExport,
  onPreview,
  previewing,
  onSaveRoi,
  roiSaving,
  onNotify,
  onDryRun,
  dryRunning,
}: DashboardViewProps) {
  const rag = useMemo(() => (data ? ragFromMetrics(data.evm.spi, data.evm.cpi) : 'Watch'), [data])
  const [openExplain, setOpenExplain] = useState<ExplainKey | null>(null)
  const [primerMetric, setPrimerMetric] = useState<PrimerMetric | null>(null)
  const [localAssumptions, setLocalAssumptions] = useState<RoiAssumption[]>(data?.roi.assumptions ?? [])
  const [selectedPreset, setSelectedPreset] = useState<string>(data?.roi.selected_preset ?? 'medium')
  const [localModifiers, setLocalModifiers] = useState<RoiModifiers>(
    data?.roi.modifiers ?? { time_saved_multiplier: 1, frequency_multiplier: 1 },
  )
  const [changeFilter, setChangeFilter] = useState<'recent' | 'all'>('recent')
  const [changeGrouping, setChangeGrouping] = useState<'chronological' | 'entity'>('chronological')
  const presetMap = useMemo(() => {
    const map = new Map<string, RoiPreset>()
    data?.roi.available_presets.forEach((preset) => {
      map.set(preset.name, preset)
    })
    return map
  }, [data])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpenExplain(null)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useEffect(() => {
    setOpenExplain(null)
    setPrimerMetric(null)
  }, [data])

  useEffect(() => {
    if (data) {
      setLocalAssumptions(cloneAssumptions(data.roi.assumptions))
      setSelectedPreset(data.roi.selected_preset)
      setLocalModifiers({ ...data.roi.modifiers })
    }
  }, [data])

  const toggleExplain = (key: ExplainKey) => {
    setOpenExplain((prev) => (prev === key ? null : key))
  }

  const renderExplain = (key: ExplainKey, id: string) => {
    if (openExplain !== key) {
      return null
    }
    const copy = EXPLAIN_COPY[key]
    return (
      <div className="info-popover" id={id} role="dialog" aria-label={copy.title}>
        <strong>{copy.title}</strong>
        <p>{copy.body}</p>
        {copy.href && (
          <a href={copy.href} target="_blank" rel="noreferrer">
            {copy.linkLabel ?? 'Learn more'}
          </a>
        )}
        <button className="button link" type="button" onClick={() => setOpenExplain(null)}>
          Close
        </button>
      </div>
    )
  }

  const handleAssumptionChange = (index: number, key: keyof RoiAssumption, value: number) => {
    setLocalAssumptions((prev) => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [key]: value }
      return updated
    })
  }

  const handlePresetChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextPreset = event.target.value
    setSelectedPreset(nextPreset)
    const preset = presetMap.get(nextPreset)
    if (preset) {
      setLocalAssumptions(cloneAssumptions(preset.assumptions))
      setLocalModifiers({ time_saved_multiplier: 1, frequency_multiplier: 1 })
    }
  }

  const handleModifierChange = (key: keyof RoiModifiers, value: number) => {
    setLocalModifiers((prev) => ({ ...prev, [key]: value }))
  }

  const handleRoiSave = async () => {
    const payload: RoiUpdateRequest = {
      preset: selectedPreset,
      modifiers: localModifiers,
      assumptions: localAssumptions,
    }
    await onSaveRoi(payload)
  }

  const preview = useMemo(() => computePreview(localAssumptions, localModifiers), [localAssumptions, localModifiers])
  const inlineAssumptions = useMemo(
    () =>
      localAssumptions.map((assumption) => {
        const frequency = assumption.frequency_per_month * localModifiers.frequency_multiplier
        const hoursSaved = assumption.hours_saved * localModifiers.time_saved_multiplier
        const annualOccurrences = frequency * 12
        const annualHours = hoursSaved * annualOccurrences * assumption.team_size
        const annualValue = annualHours * assumption.pm_hourly_cost
        return {
          name: assumption.task_name,
          frequency,
          hoursSaved,
          teamSize: assumption.team_size,
          rate: assumption.pm_hourly_cost,
          annualHours,
          annualValue,
        }
      }),
    [localAssumptions, localModifiers],
  )

  const metrics: Array<{ label: string; value: number; tooltip: string; primerKey?: PrimerMetric; docsHref?: string }> = data
    ? [
        { label: 'Planned Value (PV)', value: data.evm.pv, tooltip: 'PV (planned value) tracks scheduled work in hours.' },
        { label: 'Earned Value (EV)', value: data.evm.ev, tooltip: 'EV (earned value) reflects completed work weightings.' },
        { label: 'Actual Cost (AC)', value: data.evm.ac, tooltip: 'AC (actual cost proxy) sums actual hours.' },
        { label: 'Schedule Variance (SV)', value: data.evm.sv, tooltip: 'SV = EV - PV; negative values show schedule slip.' },
        { label: 'Cost Variance (CV)', value: data.evm.cv, tooltip: 'CV = EV - AC; negative values show overspend.' },
        {
          label: 'Cost Performance Index (CPI)',
          value: data.evm.cpi ?? 0,
          tooltip: 'CPI = EV ÷ AC; < 1.0 indicates cost pressure.',
          primerKey: 'cpi',
          docsHref: `${DOCS_BASE_URL}/docs/EVM-PRIMER.md#core-concepts`,
        },
        {
          label: 'Schedule Performance Index (SPI)',
          value: data.evm.spi ?? 0,
          tooltip: 'SPI = EV ÷ PV; < 1.0 indicates schedule pressure.',
          primerKey: 'spi',
          docsHref: `${DOCS_BASE_URL}/docs/EVM-PRIMER.md#core-concepts`,
        },
        {
          label: 'Estimate at Completion (EAC)',
          value: data.evm.eac ?? 0,
          tooltip: 'EAC = AC + (BAC - EV) ÷ CPI.',
          primerKey: 'eac',
        },
      ]
    : []

  const changeGlyph: Record<'added' | 'updated' | 'removed', string> = {
    added: '▲',
    updated: '↻',
    removed: '▼',
  }

  const sourceLookup: Record<'task' | 'risk' | 'note', string> = {
    task: 'tasks.csv',
    risk: 'risks.csv',
    note: 'status_notes.md',
  }

  const copyAssumptions = async () => {
    const header = ['| Task | Frequency/mo | Hours saved | PM hourly cost | Team size |', '| --- | --- | --- | --- | --- |']
    const rows = localAssumptions.map((assumption) => {
      const frequency = (assumption.frequency_per_month * localModifiers.frequency_multiplier).toFixed(2)
      const hours = (assumption.hours_saved * localModifiers.time_saved_multiplier).toFixed(2)
      const rate = assumption.pm_hourly_cost.toFixed(2)
      return `| ${assumption.task_name} | ${frequency} | ${hours} | $${rate} | ${assumption.team_size} |`
    })
    const lines = [
      `# ASR Copilot ROI assumptions (${selectedPreset})`,
      '',
      ...header,
      ...rows,
      '',
      `Projected annual savings: $${preview.annual.toLocaleString()}`,
      `Projected monthly savings: $${preview.monthly.toLocaleString()}`,
      `Projected annual hours reclaimed: ${preview.hours.toLocaleString()} hrs`,
    ]
    try {
      await navigator.clipboard.writeText(lines.join('\n'))
      onNotify?.('ROI assumptions copied to clipboard.')
    } catch (err) {
      onNotify?.('Clipboard copy failed. Copy manually from ROI table.')
      console.error('Clipboard copy failed', err)
    }
  }

  const handleDryRunClick = useCallback(async () => {
    try {
      await onDryRun()
    } catch (error) {
      if (onNotify) {
        onNotify('Dry-run failed. Check console logs for details.')
      }
      console.error('Dry-run simulation failed', error)
    }
  }, [onDryRun, onNotify])

  const handleDraftMitigation = async (risk: RiskListItem) => {
    const mitigationText = `Risk ${risk.id} (${risk.summary}) — mitigation owner ${risk.owner} to confirm path by ${new Date(
      risk.due_date,
    ).toLocaleDateString()}. Proposed action: reinforce vendor SLA, align dependencies, and add contingency.`
    try {
      await navigator.clipboard.writeText(mitigationText)
      onNotify?.('Mitigation draft copied to clipboard.')
    } catch (copyError) {
      console.error('Failed to copy mitigation draft', copyError)
      onNotify?.('Unable to copy mitigation draft; copy manually if needed.')
    }
  }

  const changeItems = useMemo(() => {
    if (!data) {
      return []
    }
    if (changeFilter === 'recent') {
      return data.changes.items.slice(0, 5)
    }
    return data.changes.items
  }, [changeFilter, data])

  const groupedChanges = useMemo(() => {
    if (changeGrouping === 'chronological') {
      return null
    }
    const groups = new Map<string, typeof changeItems>()
    const labels: Record<'task' | 'risk' | 'note', string> = {
      task: 'Tasks',
      risk: 'Risks',
      note: 'Status notes',
    }
    changeItems.forEach((item) => {
      const label = labels[item.entity_type]
      const current = groups.get(label) ?? []
      current.push(item)
      groups.set(label, current)
    })
    return groups
  }, [changeGrouping, changeItems])

  const renderChangeItem = (item: DashboardPayload['changes']['items'][number]) => (
    <article key={item.id + item.change_type} className={`timeline-item ${item.change_type}`}>
      <header className="timeline-header">
        <div className="timeline-title">
          <span className={`diff-pill ${item.change_type}`} aria-hidden="true">
            {changeGlyph[item.change_type]}
          </span>
          <div>
            <strong>
              {changeLabel[item.change_type]} {item.entity_type} – {item.title}
            </strong>
            <p className="timeline-subtitle">
              Source: {sourceLookup[item.entity_type]} • {new Date(item.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      </header>
      <pre>{item.detail}</pre>
    </article>
  )

  if (isLoading) {
    return (
      <div className="dashboard-grid" aria-busy="true">
        <div className="section-card skeleton" style={{ height: 120 }} />
        <div className="section-card skeleton" style={{ height: 220 }} />
        <div className="section-card skeleton" style={{ height: 260 }} />
        <div className="section-card skeleton" style={{ height: 260 }} />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="empty-state" role="status">
        <h3>No data yet</h3>
        <p>Upload your CSVs or try the sample program to see ASR Copilot in action.</p>
      </div>
    )
  }

  const automationTriggerLabel = TRIGGER_LABELS[data.automation.trigger] ?? TRIGGER_LABELS.unknown

  return (
    <>
      <div className="dashboard-grid">
      <section className="section-card" aria-labelledby="status-heading">
        <div className="status-header">
          <div>
            <div className="rag-row">
              <p className={`badge ${rag === 'On Track' ? 'track' : rag === 'Watch' ? 'watch' : 'risk'}`}>
                Overall RAG: {rag}
              </p>
              <button
                type="button"
                className="info-icon"
                aria-label="Open EVM primer for RAG"
                title="How we translate CPI/SPI into the RAG badge."
                onClick={() => setPrimerMetric('rag')}
              >
                <span aria-hidden="true">ℹ️</span>
              </button>
              <a
                className="glossary-link"
                href={`${DOCS_BASE_URL}/docs/EVM-PRIMER.md#core-concepts`}
                target="_blank"
                rel="noreferrer"
              >
                Glossary
              </a>
            </div>
            <div className="card-heading">
              <h3 id="status-heading">Program health</h3>
              <button
                className="explain-button"
                type="button"
                onClick={() => toggleExplain('evm')}
                aria-expanded={openExplain === 'evm'}
                aria-controls="evm-explain"
                title="Quick script for the CPI/SPI gauges."
              >
                <span aria-hidden="true">ⓘ</span>
                Explain this
              </button>
            </div>
            <p>{data.narrative}</p>
          </div>
          <div className="card-actions">
            <button
              className="button secondary"
              onClick={() => {
                void onPreview()
              }}
              disabled={previewing}
              title="Preview Markdown and charts before saving the export."
            >
              {previewing ? 'Previewing…' : 'Preview export'}
            </button>
            <button
              className="button primary"
              onClick={onExport}
              disabled={exporting}
              title="Save Markdown + charts to /out and trigger reveal/copy actions."
            >
              {exporting ? 'Exporting…' : 'Export Status Pack'}
            </button>
          </div>
        </div>
        {renderExplain('evm', 'evm-explain')}
        <div className="metric-grid" role="list">
          {metrics.map((metric) => (
            <article key={metric.label} className="metric-card" role="listitem">
              <div className="metric-card-header">
                <span className="metric-label">{metric.label}</span>
                {metric.primerKey && (
                  <button
                    type="button"
                    className="info-icon"
                    aria-label={`Open EVM primer for ${metric.label}`}
                    title={`Explain ${metric.label}`}
                    onClick={() => metric.primerKey && setPrimerMetric(metric.primerKey)}
                  >
                    <span aria-hidden="true">ℹ️</span>
                  </button>
                )}
              </div>
              <span className="metric-value">
                {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
              </span>
              <div className="metric-bar" aria-hidden="true">
                <div
                  className="metric-bar-fill"
                  style={{ width: `${Math.min(Math.abs(Number(metric.value)) * 10, 100)}%` }}
                />
              </div>
              <p className="metric-helper">
                {metric.tooltip}{' '}
                {metric.docsHref && (
                  <a href={metric.docsHref} target="_blank" rel="noreferrer">
                    Glossary
                  </a>
                )}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-card" aria-labelledby="risk-heading">
        <div className="card-heading">
          <h3 id="risk-heading">Top risks</h3>
          <button
            className="explain-button"
            type="button"
            onClick={() => toggleExplain('risks')}
            aria-expanded={openExplain === 'risks'}
            aria-controls="risks-explain"
            title="How we rank and narrate the risk table."
          >
            <span aria-hidden="true">ⓘ</span>
            Explain this
          </button>
        </div>
        {renderExplain('risks', 'risks-explain')}
        {data.risks.top_risks.length === 0 ? (
          <p>No risks logged. Import your risk register to populate the watchlist.</p>
        ) : (
          <div className="risk-list">
            {data.risks.top_risks.map((risk) => (
              <article key={risk.id} className="risk-item">
                <div>
                  <strong>{risk.summary}</strong>
                  <div className="risk-meta">
                    <span className={`risk-severity ${risk.status.toLowerCase()}`}>Severity: {risk.severity.toFixed(2)}</span>
                    <span>Owner: {risk.owner}</span>
                    <span>Due: {new Date(risk.due_date).toLocaleDateString()}</span>
                  </div>
                  {risk.mitigation && <p>Mitigation: {risk.mitigation}</p>}
                  <div className="risk-actions">
                    <button className="button tertiary" type="button" onClick={() => handleDraftMitigation(risk)}>
                      Draft mitigation
                    </button>
                  </div>
                </div>
                <span aria-label={`Risk status ${risk.status}`}>{risk.status}</span>
              </article>
            ))}
          </div>
        )}
        <div className="heatmap" role="img" aria-label="Risk heatmap showing probability vs impact">
          <svg viewBox="0 0 300 180" width="100%" height="180">
            <line x1="40" y1="10" x2="40" y2="150" stroke="#9db3e8" strokeWidth="1" />
            <line x1="40" y1="150" x2="290" y2="150" stroke="#9db3e8" strokeWidth="1" />
            <text x="10" y="20" fontSize="12">Impact</text>
            <text x="255" y="170" fontSize="12">Probability</text>
            {data.risks.heatmap.map((point) => {
              const x = 40 + point.probability * 240
              const y = 150 - point.impact * 25
              const radius = 8 + point.severity * 2
              return (
                <g key={point.id}>
                  <circle cx={x} cy={y} r={radius} fill="#ff6b6b" opacity={0.75} />
                  <title>
                    {point.summary} (Severity {point.severity.toFixed(2)})
                  </title>
                </g>
              )
            })}
          </svg>
          <p>Bubble size reflects urgency. Tab across points to hear severity and summary details.</p>
        </div>
      </section>

      <section className="section-card" aria-labelledby="changes-heading">
        <div className="card-heading">
          <h3 id="changes-heading">What changed since last snapshot</h3>
        </div>
        <div className="timeline-controls" role="group" aria-label="Timeline view controls">
          <div className="pill-toggle">
            <button
              type="button"
              className={`toggle-pill ${changeFilter === 'recent' ? 'active' : ''}`}
              onClick={() => setChangeFilter('recent')}
            >
              Recent (Top 5)
            </button>
            <button
              type="button"
              className={`toggle-pill ${changeFilter === 'all' ? 'active' : ''}`}
              onClick={() => setChangeFilter('all')}
            >
              Full history
            </button>
          </div>
          <div className="pill-toggle">
            <button
              type="button"
              className={`toggle-pill ${changeGrouping === 'chronological' ? 'active' : ''}`}
              onClick={() => setChangeGrouping('chronological')}
            >
              Chronological
            </button>
            <button
              type="button"
              className={`toggle-pill ${changeGrouping === 'entity' ? 'active' : ''}`}
              onClick={() => setChangeGrouping('entity')}
            >
              Group by category
            </button>
          </div>
        </div>
        {data.changes.has_changes ? (
          changeGrouping === 'entity' && groupedChanges ? (
            <div className="timeline timeline-grouped">
              {[...groupedChanges.entries()].map(([label, items]) => (
                <div key={label} className="timeline-group">
                  <h4>{label}</h4>
                  {items.map((item) => renderChangeItem(item))}
                </div>
              ))}
            </div>
          ) : (
            <div className="timeline">{changeItems.map((item) => renderChangeItem(item))}</div>
          )
        ) : (
          <p>No changes detected yet. Once we have at least two uploads, we’ll highlight deltas here.</p>
        )}
        <p className="timeline-callout">
          We compare today’s snapshot to yesterday’s to highlight deltas (scope, cost, schedule, risks).
        </p>
      </section>

      <section className="section-card" aria-labelledby="roi-heading">
        <div className="card-heading roi-card-heading">
          <h3 id="roi-heading">Show me the ROI</h3>
          <details className="inline-explain" aria-label="Explain the ROI calculation">
            <summary>Explain this</summary>
            <div className="inline-explain-body" id="roi-inline-explain">
              <p>
                Annual savings = Σ((Hours saved × time multiplier) × team size × (Frequency/mo × frequency multiplier × 12)
                × hourly rate).
              </p>
              <p>
                Current totals: <strong>{formatCurrency(preview.annual)}</strong> per year /{' '}
                <strong>{formatHours(preview.hours)}</strong>.
              </p>
              <ul className="inline-explain-list">
                {inlineAssumptions.map((item) => (
                  <li key={item.name}>
                    {item.name}: {item.frequency.toFixed(1)}/mo × {item.hoursSaved.toFixed(1)} hrs × team {item.teamSize} ×{' '}
                    {formatCurrency(item.rate)} = {item.annualHours.toFixed(1)} hrs/year ({formatCurrency(item.annualValue)}).
                  </li>
                ))}
              </ul>
              <p className="inline-explain-tip">Sliders adjust the time and frequency multipliers before we sum the roll-up.</p>
              <a href={`${DOCS_BASE_URL}/WHY.md`} target="_blank" rel="noreferrer">
                Read the ROI value story
              </a>
            </div>
          </details>
        </div>
        <div className="roi-preset">
          <label htmlFor="roi-preset-select">Complexity preset</label>
          <select id="roi-preset-select" value={selectedPreset} onChange={handlePresetChange}>
            {data.roi.available_presets.map((preset) => (
              <option key={preset.name} value={preset.name}>
                {preset.label}
              </option>
            ))}
          </select>
          <p className="preset-description">{presetMap.get(selectedPreset)?.description}</p>
        </div>
        <div className="roi-summary">
          <p>
            Projected annual savings: <strong>{formatCurrency(preview.annual)}</strong> • Monthly savings:{' '}
            <strong>{formatCurrency(preview.monthly)}</strong> • Annual hours reclaimed:{' '}
            <strong>{formatHours(preview.hours)}</strong>
          </p>
        </div>
        <div className="roi-sliders">
          <label>
            Time saved multiplier ({Math.round(localModifiers.time_saved_multiplier * 100)}%)
            <input
              type="range"
              min={0.6}
              max={1.4}
              step={0.05}
              value={localModifiers.time_saved_multiplier}
              onChange={(event) => handleModifierChange('time_saved_multiplier', Number(event.target.value))}
            />
          </label>
          <label>
            Frequency multiplier ({Math.round(localModifiers.frequency_multiplier * 100)}%)
            <input
              type="range"
              min={0.6}
              max={1.4}
              step={0.05}
              value={localModifiers.frequency_multiplier}
              onChange={(event) => handleModifierChange('frequency_multiplier', Number(event.target.value))}
            />
          </label>
        </div>
        <div className="roi-grid">
          {localAssumptions.map((assumption, index) => (
            <label key={assumption.task_name}>
              {assumption.task_name}
              <input
                type="number"
                min={0}
                step="0.1"
                value={assumption.frequency_per_month}
                onChange={(event) => handleAssumptionChange(index, 'frequency_per_month', Number(event.target.value))}
                aria-label={`${assumption.task_name} frequency per month`}
              />
              <input
                type="number"
                min={0}
                step="0.1"
                value={assumption.hours_saved}
                onChange={(event) => handleAssumptionChange(index, 'hours_saved', Number(event.target.value))}
                aria-label={`${assumption.task_name} hours saved`}
              />
              <input
                type="number"
                min={0}
                step="1"
                value={assumption.pm_hourly_cost}
                onChange={(event) => handleAssumptionChange(index, 'pm_hourly_cost', Number(event.target.value))}
                aria-label={`${assumption.task_name} PM hourly cost`}
              />
              <input
                type="number"
                min={1}
                step="1"
                value={assumption.team_size}
                onChange={(event) => handleAssumptionChange(index, 'team_size', Number(event.target.value))}
                aria-label={`${assumption.task_name} team size`}
              />
            </label>
          ))}
        </div>
        <div className="cta-group" style={{ justifyContent: 'flex-end', gap: '12px' }}>
          <button className="button ghost" type="button" onClick={copyAssumptions}>
            Copy assumptions
          </button>
          <button
            className="button secondary"
            onClick={() => {
              const preset = presetMap.get(selectedPreset)
              if (preset) {
                setLocalAssumptions(cloneAssumptions(preset.assumptions))
                setLocalModifiers({ time_saved_multiplier: 1, frequency_multiplier: 1 })
              }
            }}
          >
            Reset to defaults
          </button>
          <button className="button primary" onClick={handleRoiSave} disabled={roiSaving}>
            {roiSaving ? 'Saving…' : 'Save ROI assumptions'}
          </button>
        </div>
      </section>

      <section className="section-card automation-card" aria-labelledby="automation-heading">
        <div className="card-heading automation-heading">
          <h3 id="automation-heading">Automation loop</h3>
          <button className="button secondary" type="button" onClick={handleDryRunClick} disabled={dryRunning}>
            {dryRunning ? 'Simulating…' : 'Dry-run schedule'}
          </button>
        </div>
        <p className="automation-meta">
          Last run: {data.automation.last_run ? new Date(data.automation.last_run).toLocaleString() : 'Never'} • Trigger:{' '}
          {automationTriggerLabel}
        </p>
        <div className="automation-steps">
          {data.automation.steps.map((step) => (
            <article key={step.key} className={`automation-step ${step.status}`}>
              <div className="step-header">
                <span className="status-indicator" aria-hidden="true" />
                <strong>{step.title}</strong>
                {typeof step.duration_ms === 'number' && step.duration_ms >= 0 && (
                  <span className="step-duration">{(step.duration_ms / 1000).toFixed(1)}s</span>
                )}
              </div>
              <p>{step.note ?? 'Awaiting first run.'}</p>
              <span className="step-timestamp">
                {step.last_run ? new Date(step.last_run).toLocaleString() : 'Not run yet'}
              </span>
            </article>
          ))}
        </div>
      </section>
      </div>
      {primerMetric && <EvmPrimerModal metric={primerMetric} onClose={() => setPrimerMetric(null)} />}
    </>
  )
}
