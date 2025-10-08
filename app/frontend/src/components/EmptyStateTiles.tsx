interface EmptyStateTilesProps {
  onShowGuided: () => void
  onLoadSample: () => void | Promise<void>
  onFocusUpload: () => void
  safeModeDocUrl: string
}

export function EmptyStateTiles({ onShowGuided, onLoadSample, onFocusUpload, safeModeDocUrl }: EmptyStateTilesProps) {
  return (
    <section className="empty-tiles" aria-label="Getting started options">
      <article className="empty-tile" aria-label="Try Guided Mode tile">
        <h3>Guided Mode (no files)</h3>
        <p>Pick from curated telecom, cloud, or device scenarios. Safe Mode stays on—perfect for executive click-throughs.</p>
        <div className="tile-actions">
          <button
            className="button primary"
            type="button"
            onClick={onShowGuided}
            title="Scroll to the Guided Mode cards and launch a scenario with one click."
          >
            Explore Guided Mode
          </button>
        </div>
      </article>
      <article className="empty-tile" aria-label="Load sample data tile">
        <h3>Classic sample dataset</h3>
        <p>Prefer the original portfolio? Load the bundled telecom program and follow the guided tour script.</p>
        <div className="tile-actions">
          <button
            className="button primary"
            type="button"
            onClick={onLoadSample}
            title="One click loads the bundled telecom program so you can narrate the story without prep."
          >
            Load sample data
          </button>
        </div>
      </article>
      <article className="empty-tile" aria-label="Upload your files tile">
        <h3>Upload your CSV/Markdown</h3>
        <p>Use your backlog, risk register, and status notes to generate CPI/SPI, risks, ROI, and exports.</p>
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
      <article className="empty-tile" aria-label="Safe Mode details tile">
        <h3>See how we keep data local</h3>
        <p>Safe Mode is on by default. No outbound calls, tokens stay off disk, and adapters run in mock mode.</p>
        <div className="tile-actions">
          <a
            className="button tertiary"
            href={safeModeDocUrl}
            target="_blank"
            rel="noreferrer"
            title="Opens the README section that explains Safe Mode, adapters, and how credentials are handled."
          >
            Details
          </a>
        </div>
      </article>
    </section>
  )
}
