import { useEffect, useRef } from 'react'
import type { MouseEvent as ReactMouseEvent } from 'react'

export type PrimerMetric = 'rag' | 'cpi' | 'spi' | 'eac'

interface EvmPrimerModalProps {
  metric: PrimerMetric
  onClose: () => void
}

const DOCS_URL = 'https://github.com/jlov7/ASR-Copilot/blob/main/docs/EVM-PRIMER.md'

interface PrimerContent {
  title: string
  lede: string
  formula: string
  points: string[]
  tip?: string
  href: string
  linkLabel: string
}

const PRIMER_CONTENT: Record<PrimerMetric, PrimerContent> = {
  rag: {
    title: 'RAG badge (overall health)',
    lede: 'We blend CPI (cost) and SPI (schedule) into a single red/amber/green badge so execs see pressure instantly.',
    formula: 'Green when CPI ≥ 1.0 and SPI ≥ 1.0 • Amber when either falls between 0.95–0.99 • Red below 0.95 or missing baselines',
    points: [
      'Green = both CPI and SPI at or above 1.0.',
      'Amber = CPI or SPI in the 0.95–0.99 band triggers watch status.',
      'Red = any metric below 0.95 or missing baselines; escalate with mitigation.',
    ],
    tip: 'This mirrors PMO guardrails from the EVM primer so the badge feels defensible to execs.',
    href: `${DOCS_URL}#worked-example`,
    linkLabel: 'See the worked example',
  },
  cpi: {
    title: 'Cost Performance Index (CPI)',
    lede: 'Shows how efficiently the program is spending by comparing earned value to actual cost.',
    formula: 'CPI = Earned Value (EV) ÷ Actual Cost (AC)',
    points: [
      '> 1.0 = under budget; celebrate and maintain guardrails.',
      '0.95–1.0 = cost watch; align spend with scope adjustments.',
      '< 0.95 = cost pressure; escalate with finance/vendor owners.',
    ],
    tip: 'Safe Mode treats hours as a cost proxy. Live adapters can swap in actual dollars later.',
    href: `${DOCS_URL}#core-concepts`,
    linkLabel: 'Open CPI primer',
  },
  spi: {
    title: 'Schedule Performance Index (SPI)',
    lede: 'Compares earned value to the planned baseline to flag schedule drag.',
    formula: 'SPI = Earned Value (EV) ÷ Planned Value (PV)',
    points: [
      '> 1.0 = ahead of schedule; capture lessons and re-plan slack.',
      '0.95–1.0 = schedule watch; nudge workstream owners.',
      '< 0.95 = schedule slip; pull risks into mitigation plans.',
    ],
    tip: 'SPI pairs with CPI to drive the RAG banner and the “What changed” timeline focus.',
    href: `${DOCS_URL}#core-concepts`,
    linkLabel: 'Open SPI primer',
  },
  eac: {
    title: 'Estimate at Completion (EAC)',
    lede: 'Forecasts final cost if today’s performance continues, using CPI to project remaining spend.',
    formula: 'EAC = AC + (Budget at Completion − Earned Value) ÷ CPI',
    points: [
      'Compare EAC to BAC to quantify expected overruns or underruns.',
      'Improving CPI pulls EAC down; deteriorating CPI pushes it up.',
      'Safe Mode uses hours as the cost proxy; live adapters can provide financial actuals.',
    ],
    tip: 'Pair EAC with ROI savings to show the delta automation delivers to executive stakeholders.',
    href: `${DOCS_URL}#core-concepts`,
    linkLabel: 'Open EAC primer',
  },
}

export function EvmPrimerModal({ metric, onClose }: EvmPrimerModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const content = PRIMER_CONTENT[metric]
  const labelId = `primer-title-${metric}`
  const descriptionId = `primer-description-${metric}`

  useEffect(() => {
    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  useEffect(() => {
    dialogRef.current?.focus()
  }, [metric])

  const handleBackdropClick = (event: ReactMouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="modal-backdrop primer-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby={labelId}
      aria-describedby={descriptionId}
      onClick={handleBackdropClick}
    >
      <article
        className="primer-modal"
        role="document"
        tabIndex={-1}
        ref={dialogRef}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="primer-header">
          <h3 id={labelId}>{content.title}</h3>
          <button className="button ghost" type="button" onClick={onClose} aria-label="Close EVM primer">
            ✕
          </button>
        </header>
        <p id={descriptionId}>{content.lede}</p>
        <p className="primer-formula">
          <strong>Formula:</strong> <code>{content.formula}</code>
        </p>
        <ul className="primer-points">
          {content.points.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
        {content.tip && <p className="primer-tip">{content.tip}</p>}
        <a href={content.href} target="_blank" rel="noreferrer">
          {content.linkLabel}
        </a>
      </article>
    </div>
  )
}
