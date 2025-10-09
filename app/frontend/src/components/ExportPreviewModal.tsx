import { useEffect, useId } from 'react'
import type { StatusPackPreview } from '../types'

interface ExportPreviewModalProps {
  open: boolean
  loading: boolean
  preview: StatusPackPreview | null
  error?: string | null
  onClose: () => void
}

export function ExportPreviewModal({ open, loading, preview, error, onClose }: ExportPreviewModalProps) {
  const headingId = useId()

  useEffect(() => {
    if (!open) {
      return undefined
    }
    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  if (!open) {
    return null
  }

  const handleCopy = async () => {
    if (!preview?.markdown) return
    try {
      await navigator.clipboard.writeText(preview.markdown)
    } catch (copyError) {
      console.error('Failed to copy preview markdown', copyError)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby={headingId}>
        <header className="modal-header">
          <h3 id={headingId}>Status Pack Preview</h3>
          <button type="button" className="button ghost" onClick={onClose} aria-label="Close preview modal">
            ✕
          </button>
        </header>
        {loading && <p className="modal-status">Generating preview…</p>}
        {!loading && error && (
          <p className="modal-error" role="alert">
            {error}
          </p>
        )}
        {!loading && preview && (
          <div className="modal-body">
            <div className="modal-actions">
              <button type="button" className="button secondary" onClick={handleCopy}>
                Copy Markdown
              </button>
              <span className="modal-hash">Dataset hash {preview.dataset_hash.slice(0, 8)}</span>
            </div>
            <details className="markdown-preview">
              <summary>Executive Markdown (toggle)</summary>
              <pre>
                <code>{preview.markdown}</code>
              </pre>
            </details>
            <div className="chart-preview-grid">
              {preview.charts.map((chart) => (
                <figure key={chart.name} className="chart-preview">
                  <img src={chart.data_uri} alt={chart.description ?? chart.name} />
                  <figcaption>{chart.description ?? chart.name}</figcaption>
                </figure>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
