import { useEffect } from 'react'

interface WelcomeModalProps {
  open: boolean
  onClose: () => void
  onGuided: () => void
  onUpload: () => void
  onLearnMore: () => void
}

export function WelcomeModal({ open, onClose, onGuided, onUpload, onLearnMore }: WelcomeModalProps) {
  useEffect(() => {
    if (!open) return
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  if (!open) {
    return null
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <div className="welcome-modal" role="dialog" aria-modal="true" aria-labelledby="welcome-heading">
        <header>
          <h2 id="welcome-heading">Welcome to ASR Copilot</h2>
          <p className="welcome-subheading">Your executive-status copilot ships with a no-integration demo path.</p>
        </header>
        <ul className="welcome-promises">
          <li>
            <strong>No integrations needed.</strong> Instant Demo preloads curated datasets so anyone can explore outcomes
            in seconds.
          </li>
          <li>
            <strong>Safe Mode stays on.</strong> Demo runs offline-only with mock adapters; nothing leaves your machine.
          </li>
          <li>
            <strong>Executive pack in one click.</strong> RAG → EVM → Risks → What changed → ready-to-share exports.
          </li>
        </ul>
        <div className="welcome-actions">
          <button className="button primary" type="button" onClick={onGuided}>
            Launch Instant Demo
          </button>
          <button className="button secondary" type="button" onClick={onUpload}>
            Upload files
          </button>
          <button className="button link" type="button" onClick={onLearnMore}>
            Learn how this saves time
          </button>
        </div>
        <button className="button ghost welcome-dismiss" type="button" onClick={onClose}>
          Skip for now
        </button>
      </div>
    </div>
  )
}
