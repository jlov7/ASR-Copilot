interface EmptyStateTilesProps {
  onShowGuided: () => void
  onLoadSample: () => void | Promise<void>
  onFocusUpload: () => void
  onFocusAdapters: () => void
  safeModeDocUrl: string
  sampleLoading?: boolean
}

export function EmptyStateTiles({
  onShowGuided,
  onLoadSample,
  onFocusUpload,
  onFocusAdapters,
  safeModeDocUrl,
  sampleLoading = false,
}: EmptyStateTilesProps) {
  return (
    <section className="empty-tiles" aria-label="Getting started options">
      <article className="empty-tile" aria-label="Load sample portfolio tile">
        <h3>Load sample portfolio</h3>
        <p>Launch the telco modernization program with Data Health Score, chase preview, and compliance panel in seconds.</p>
        <div className="tile-actions">
          <button
            className="button primary"
            type="button"
            onClick={onLoadSample}
            disabled={sampleLoading}
            title="One click loads the bundled telecom program so you can narrate the story without prep."
            aria-busy={sampleLoading}
          >
            {sampleLoading ? 'Loading…' : 'Load sample data'}
          </button>
        </div>
      </article>
      <article className="empty-tile" aria-label="Connect read-only adapters tile">
        <h3>Connect read-only adapters</h3>
        <p>Walk through Jira, ServiceNow, or Planview connectors. Safe Mode enforces read-only guardrails until you flip the switch.</p>
        <div className="tile-actions">
          <button
            className="button secondary"
            type="button"
            onClick={onFocusAdapters}
            title="Scroll to the connectors panel and review adapter modes."
          >
            View connectors
          </button>
          <a className="button ghost" href={safeModeDocUrl} target="_blank" rel="noreferrer" title="Open Safe Mode documentation">
            Safe Mode details
          </a>
        </div>
      </article>
      <article className="empty-tile" aria-label="Upload your files tile">
        <h3>Upload your CSV/Markdown</h3>
        <p>Use your backlog, risk register, and status notes to generate EVM deltas, RAID updates, Data Health Score, and audit exports.</p>
        <details className="schema-details">
          <summary>See sample schema</summary>
          <ul>
            <li>
              <strong>tasks.csv</strong> → <code>id,title,owner,status,start_date,finish_date,planned_hours,actual_hours</code>
            </li>
            <li>
              <strong>risks.csv</strong> → <code>id,summary,probability,impact,owner,due_date,mitigation,status</code>
            </li>
            <li>
              <strong>status_notes.md</strong> → dated sections with highlights/blockers.
            </li>
            <li>
              <strong>evm_baseline.csv</strong> → <code>date,pv,ev,ac</code>
            </li>
          </ul>
          <p>
            Full details live in{' '}
            <a
              href="https://github.com/jlov7/ASR-Copilot/blob/main/docs/DATA-SCHEMA.md"
              target="_blank"
              rel="noreferrer"
            >
              docs/DATA-SCHEMA.md
            </a>
            .
          </p>
        </details>
        <div className="tile-actions">
          <button
            className="button secondary"
            type="button"
            onClick={onFocusUpload}
            title="Jump to the upload form; we validate CSV/Markdown formats and keep data local."
          >
            Jump to upload form
          </button>
        </div>
      </article>
      <article className="empty-tile" aria-label="Guided scenarios tile">
        <h3>Explore guided scenarios</h3>
        <p>Pick a curated telecom, cloud migration, or device rollout playlist with built-in narration cues.</p>
        <div className="tile-actions">
          <button
            className="button tertiary"
            type="button"
            onClick={onShowGuided}
            title="Scroll to the guided scenarios section and pick a playlist."
          >
            Browse scenarios
          </button>
        </div>
      </article>
    </section>
  )
}
