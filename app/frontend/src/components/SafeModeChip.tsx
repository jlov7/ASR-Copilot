import { useId, useState } from 'react'

interface SafeModeChipProps {
  safeMode: boolean
  disabled?: boolean
  onToggle: (value: boolean) => void
  docUrl: string
}

export function SafeModeChip({ safeMode, onToggle, disabled = false, docUrl }: SafeModeChipProps) {
  const tooltipId = useId()
  const [showTooltip, setShowTooltip] = useState(false)
  const label = safeMode ? 'SAFE MODE: ON' : 'SAFE MODE: OFF'
  const statusClass = safeMode ? 'on' : 'off'

  const handleToggle = () => {
    if (disabled) return
    onToggle(!safeMode)
  }

  return (
    <div
      className={`safe-mode-chip ${statusClass}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <button
        type="button"
        className="chip-button"
        aria-pressed={safeMode}
        aria-describedby={tooltipId}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        onClick={handleToggle}
        disabled={disabled}
      >
        <span className="chip-indicator" aria-hidden="true" />
        <span className="chip-label">{label}</span>
      </button>
      <div
        id={tooltipId}
        role="tooltip"
        className="safe-mode-tooltip"
        data-visible={showTooltip && !disabled}
      >
        <p>
          Safe Mode keeps adapters in mock mode, blocks outbound requests, and stores exports on this device.
        </p>
        <a href={docUrl} target="_blank" rel="noreferrer">
          Learn more
        </a>
      </div>
    </div>
  )
}
