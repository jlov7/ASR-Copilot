interface FirstRunBannerProps {
  onLaunchDemo: () => void
  onSeeSchema: () => void
}

export function FirstRunBanner({ onLaunchDemo, onSeeSchema }: FirstRunBannerProps) {
  return (
    <div className="first-run-banner" role="note" aria-live="polite">
      <div>
        <p className="first-run-title">No uploads needed—start with Instant Demo.</p>
        <p className="first-run-body">
          Safe Mode keeps data local while you explore CPI/SPI, risks, and the export flow. Ready to use your own files?
          Check the expected schema first.
        </p>
      </div>
      <div className="first-run-actions">
        <button type="button" className="button primary" onClick={onLaunchDemo}>
          Launch Instant Demo
        </button>
        <button type="button" className="button secondary" onClick={onSeeSchema}>
          Review schema
        </button>
      </div>
    </div>
  )
}
