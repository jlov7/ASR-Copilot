export interface GuidedScenario {
  id: '5g' | 'cloud' | 'cpe'
  title: string
  description: string
  highlight: string
  seed: number
}

const SCENARIOS: GuidedScenario[] = [
  {
    id: '5g',
    title: '5G Rollout',
    description: 'Sites, vendor readiness, and migration gates for a telecom program.',
    highlight: 'Shows RAG + CPI/SPI against tower deployment cadence.',
    seed: 42,
  },
  {
    id: 'cloud',
    title: 'Cloud Migration',
    description: 'Wave planning, landing zone guardrails, and CAB timelines.',
    highlight: 'Spot schedule risk on networking and change boards instantly.',
    seed: 17,
  },
  {
    id: 'cpe',
    title: 'CPE Swap',
    description: 'Firmware certification, field crew staffing, and customer comms.',
    highlight: 'Track pilot readiness and logistics sequenced for exec readouts.',
    seed: 7,
  },
]

interface GuidedModeProps {
  busy: boolean
  onLaunchScenario: (scenario: GuidedScenario) => Promise<void> | void
}

export function GuidedMode({ busy, onLaunchScenario }: GuidedModeProps) {
  return (
    <section className="guided-mode" aria-labelledby="instant-demo-heading">
      <header className="guided-mode-header">
        <h3 id="instant-demo-heading">Instant Demo (no files needed)</h3>
        <p>
          Pick a scenario to preload curated backlog, risks, and notes. Safe Mode is locked on—perfect for executive
          previews.
        </p>
      </header>
      <div className="guided-grid" role="list">
        {SCENARIOS.map((scenario) => (
          <article key={scenario.id} className="guided-card" role="listitem">
            <header>
              <h4>{scenario.title}</h4>
            </header>
            <p>{scenario.description}</p>
            <p className="guided-highlight">{scenario.highlight}</p>
            <button
              type="button"
              className="button primary"
              disabled={busy}
              onClick={() => onLaunchScenario(scenario)}
              aria-busy={busy}
            >
              {busy ? 'Loading…' : 'Launch scenario'}
            </button>
          </article>
        ))}
      </div>
      {busy && (
        <p className="guided-status" role="status">
          Loading guided dataset… Executive dashboard will refresh automatically.
        </p>
      )}
    </section>
  )
}

export function getGuidedScenarios(): GuidedScenario[] {
  return SCENARIOS
}
