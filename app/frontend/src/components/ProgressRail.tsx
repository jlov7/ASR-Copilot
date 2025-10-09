import type { AutomationStepStatus } from '../types'

interface ProgressRailProps {
  steps?: AutomationStepStatus[]
}

const STEP_ORDER: Array<{
  key: AutomationStepStatus['key']
  label: string
  description: string
}> = [
  { key: 'ingestion', label: 'Ingest', description: 'Load Instant Demo or upload CSV/MD' },
  { key: 'analytics', label: 'Analyze', description: 'Compute CPI/SPI, risks, deltas' },
  { key: 'narrative', label: 'Narrate', description: 'Assemble executive-ready summary' },
  { key: 'export', label: 'Export', description: 'Generate Markdown + chart bundle' },
]

type StepVisualState = 'complete' | 'current' | 'pending' | 'error' | 'mock'

function resolveVisualState(step?: AutomationStepStatus): StepVisualState {
  if (!step) return 'pending'
  if (step.status === 'error') return 'error'
  if (step.status === 'mock') return 'mock'
  if (step.status === 'ok') return 'complete'
  return 'pending'
}

export function ProgressRail({ steps = [] }: ProgressRailProps) {
  const orderedSteps = STEP_ORDER.map((definition) => {
    const match = steps.find((item) => item.key === definition.key)
    const note =
      match?.status === 'mock'
        ? 'Safe Mode dry-run (mock adapters).'
        : match?.note ?? 'Awaiting first run.'
    return {
      ...definition,
      note,
      lastRun: match?.last_run ?? null,
      duration: match?.duration_ms ?? null,
      rawStatus: match?.status ?? 'pending',
      visual: resolveVisualState(match),
    }
  })

  const firstPendingIndex = orderedSteps.findIndex((item) => item.visual === 'pending')
  if (firstPendingIndex >= 0) {
    orderedSteps[firstPendingIndex].visual = orderedSteps[firstPendingIndex].rawStatus === 'pending' ? 'current' : orderedSteps[firstPendingIndex].visual
  }

  return (
    <section className="progress-rail" aria-label="Automation progress overview">
      {orderedSteps.map((step) => (
        <article key={step.key} className={`progress-step ${step.visual}`}>
          <header>
            <span className="progress-dot" aria-hidden="true" />
            <span className="progress-label">{step.label}</span>
          </header>
          <p className="progress-description">{step.description}</p>
          <p className="progress-note">
            {step.visual === 'complete' && step.lastRun
              ? `Last run ${new Date(step.lastRun).toLocaleString()}`
              : step.note}
          </p>
        </article>
      ))}
    </section>
  )
}
