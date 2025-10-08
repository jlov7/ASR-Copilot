interface PrivacyPanelProps {
  onPurge: () => Promise<void> | void
  purging: boolean
}

export function PrivacyPanel({ onPurge, purging }: PrivacyPanelProps) {
  return (
    <section className="section-card privacy-card" aria-labelledby="privacy-heading">
      <div className="card-heading">
        <h3 id="privacy-heading">Settings → Privacy</h3>
      </div>
      <p className="privacy-copy">
        Delete cached uploads, ROI snapshots, exports, and logs from this device after a demo or screen share.
      </p>
      <div className="privacy-actions">
        <button
          className="button secondary"
          type="button"
          onClick={onPurge}
          disabled={purging}
          aria-busy={purging}
        >
          {purging ? 'Purging…' : 'Purge local data'}
        </button>
        <span>
          Clears <code>/data/cache</code>, <code>/out</code>, and ROI state so nothing sensitive lingers.
        </span>
      </div>
    </section>
  )
}
