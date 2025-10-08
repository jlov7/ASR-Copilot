import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import type {
  DashboardPayload,
  RAGState,
  RoiAssumption,
  RoiModifiers,
  RoiPreset,
  RoiUpdateRequest,
} from '../types'

interface DashboardViewProps {
  data?: DashboardPayload
  isLoading: boolean
  exporting: boolean
  onExport: () => Promise<void>
  onSaveRoi: (payload: RoiUpdateRequest) => Promise<void>
  roiSaving: boolean
  onNotify?: (message: string) => void
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

export function DashboardView({ data, isLoading, exporting, onExport, onSaveRoi, roiSaving, onNotify }: DashboardViewProps) {
  const rag = useMemo(() => (data ? ragFromMetrics(data.evm.spi, data.evm.cpi) : 'Watch'), [data])
  const [localAssumptions, setLocalAssumptions] = useState<RoiAssumption[]>(data?.roi.assumptions ?? [])
  const [selectedPreset, setSelectedPreset] = useState<string>(data?.roi.selected_preset ?? 'medium')
  const [localModifiers, setLocalModifiers] = useState<RoiModifiers>(
    data?.roi.modifiers ?? { time_saved_multiplier: 1, frequency_multiplier: 1 },
  )
  const presetMap = useMemo(() => {
    const map = new Map<string, RoiPreset>()
    data?.roi.available_presets.forEach((preset) => {
      map.set(preset.name, preset)
    })
    return map
  }, [data])

  useEffect(() => {
    if (data) {
      setLocalAssumptions(cloneAssumptions(data.roi.assumptions))
      setSelectedPreset(data.roi.selected_preset)
      setLocalModifiers({ ...data.roi.modifiers })
    }
  }, [data])

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

  const metrics = data
    ? [
        { label: 'Planned Value (PV)', value: data.evm.pv, tooltip: 'PV (planned value) tracks scheduled work in hours.' },
        { label: 'Earned Value (EV)', value: data.evm.ev, tooltip: 'EV (earned value) reflects completed work weightings.' },
        { label: 'Actual Cost (AC)', value: data.evm.ac, tooltip: 'AC (actual cost proxy) sums actual hours.' },
        { label: 'Schedule Variance (SV)', value: data.evm.sv, tooltip: 'SV = EV - PV; negative values show schedule slip.' },
        { label: 'Cost Variance (CV)', value: data.evm.cv, tooltip: 'CV = EV - AC; negative values show overspend.' },
        { label: 'CPI', value: data.evm.cpi ?? 0, tooltip: 'CPI = EV ÷ AC; < 1.0 indicates cost pressure.' },
        { label: 'SPI', value: data.evm.spi ?? 0, tooltip: 'SPI = EV ÷ PV; < 1.0 indicates schedule pressure.' },
        { label: 'Estimate at Completion (EAC)', value: data.evm.eac ?? 0, tooltip: 'EAC = AC + (BAC - EV) ÷ CPI.' },
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

  return (
    <div className="dashboard-grid">
      <section className="section-card" aria-labelledby="status-heading">
        <div className="status-header">
          <div>
            <p className={`badge ${rag === 'On Track' ? 'track' : rag === 'Watch' ? 'watch' : 'risk'}`}>
              Overall RAG: {rag}
            </p>
            <h3 id="status-heading">Program health</h3>
            <p>{data.narrative}</p>
          </div>
          <div>
            <button className="button primary" onClick={onExport} disabled={exporting}>
              {exporting ? 'Exporting…' : 'Export Status Pack'}
            </button>
          </div>
        </div>
        <div className="metric-grid" role="list">
          {metrics.map((metric) => (
            <article key={metric.label} className="metric-card" role="listitem" title={metric.tooltip}>
              <span className="metric-label">{metric.label}</span>
              <span className="metric-value">
                {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
              </span>
              <div className="metric-bar" aria-hidden="true">
                <div
                  className="metric-bar-fill"
                  style={{ width: `${Math.min(Math.abs(Number(metric.value)) * 10, 100)}%` }}
                />
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section-card" aria-labelledby="risk-heading">
        <h3 id="risk-heading">Top risks</h3>
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
        <h3 id="changes-heading">What changed since last snapshot</h3>
        {data.changes.has_changes ? (
          <div className="timeline">
            {data.changes.items.slice(0, 5).map((item) => (
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
                      <p className="timeline-subtitle">Source: {sourceLookup[item.entity_type]} • {new Date(item.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                </header>
                <pre>{item.detail}</pre>
              </article>
            ))}
          </div>
        ) : (
          <p>No changes detected yet. Once we have at least two uploads, we’ll highlight deltas here.</p>
        )}
      </section>

      <section className="section-card" aria-labelledby="roi-heading">
        <h3 id="roi-heading">Show me the ROI</h3>
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
    </div>
  )
}
