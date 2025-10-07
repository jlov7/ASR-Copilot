import { useEffect, useRef } from 'react'
import type { KeyboardEvent, MouseEvent } from 'react'

interface TourModalProps {
  open: boolean
  stepIndex: number
  onNext: () => void
  onPrev: () => void
  onClose: () => void
}

const steps = [
  {
    title: 'Upload once, align instantly.',
    body: 'Drop in your backlog, risk register, and status notes. Safe Mode keeps everything local.',
  },
  {
    title: 'Know your CPI/SPI pulse.',
    body: 'The status header highlights schedule and cost health with CPI/SPI gauges and variance.',
  },
  {
    title: 'Triage the top risks fast.',
    body: 'Focus on the highest severity risks and mitigation owners with due-date urgency cues.',
  },
  {
    title: 'See what changed since yesterday.',
    body: 'The timeline shows new, updated, and resolved items using deterministic diffs.',
  },
  {
    title: 'Prove ROI with defensible numbers.',
    body: 'Tune assumptions to quantify annual time saved, perfect for rationalization decks.',
  },
]

export function TourModal({ open, stepIndex, onNext, onPrev, onClose }: TourModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const step = steps[stepIndex]

  const handleBackdropClick = (event: MouseEvent<HTMLButtonElement>) => {
    if (event.currentTarget === event.target) {
      onClose()
    }
  }

  const handleBackdropKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Escape') {
      onClose()
    }
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onClose()
    }
  }

  useEffect(() => {
    if (open && dialogRef.current) {
      dialogRef.current.focus()
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    if (open) {
      window.addEventListener('keydown', handleKeyDown)
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [open, onClose])

  if (!open) {
    return null
  }

  return (
    <button
      type="button"
      className="modal-backdrop"
      aria-label="Close guided tour"
      onClick={handleBackdropClick}
      onKeyDown={handleBackdropKeyDown}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tour-title"
        tabIndex={-1}
        ref={dialogRef}
      >
        <div className="modal-nav">
          <h2 id="tour-title">Guided tour</h2>
          <div className="modal-progress" aria-hidden="true">
            {steps.map((_, idx) => (
              <span key={idx} className={idx === stepIndex ? 'active' : ''} />
            ))}
          </div>
        </div>
        <article>
          <h3>{step.title}</h3>
          <p>{step.body}</p>
        </article>
        <div className="cta-group">
          <button className="button ghost" onClick={onClose}>
            Skip tour
          </button>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
            <button className="button secondary" onClick={onPrev} disabled={stepIndex === 0}>
              Back
            </button>
            <button className="button primary" onClick={onNext}>
              {stepIndex === steps.length - 1 ? 'Done – take me to the dashboard' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </button>
  )
}
