import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'

interface ToastAction {
  label: string
  onClick: () => void | Promise<void>
}

interface ToastBarProps {
  message: string
  detail?: ReactNode
  tone?: 'info' | 'success' | 'error'
  actions?: ToastAction[]
  onClose: () => void
  path?: string
  onCopyPath?: (path: string) => void | Promise<void>
}

export function ToastBar({ message, detail, tone = 'info', actions = [], onClose, path, onCopyPath }: ToastBarProps) {
  const [copied, setCopied] = useState(false)
  const copyTimer = useRef<number | null>(null)

  useEffect(() => {
    setCopied(false)
    if (copyTimer.current !== null) {
      window.clearTimeout(copyTimer.current)
      copyTimer.current = null
    }
  }, [path])

  useEffect(() => {
    return () => {
      if (copyTimer.current !== null) {
        window.clearTimeout(copyTimer.current)
      }
    }
  }, [])

  const handlePathClick = async () => {
    if (!path) return
    try {
      if (onCopyPath) {
        await onCopyPath(path)
      } else if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(path)
      }
      setCopied(true)
      if (copyTimer.current !== null) {
        window.clearTimeout(copyTimer.current)
      }
      copyTimer.current = window.setTimeout(() => {
        setCopied(false)
        copyTimer.current = null
      }, 2000)
    } catch (error) {
      console.error('Failed to copy export path', error)
    }
  }

  return (
    <div className={`toast ${tone}`} role="status" aria-live="polite">
      <div className="toast-body">
        <strong>{message}</strong>
        {detail && <div className="toast-detail">{detail}</div>}
        {path && (
          <div className="toast-detail toast-path-row">
            <span>Saved to</span>
            <button type="button" className="toast-path" onClick={handlePathClick} title="Click to copy path">
              <code>{path}</code>
            </button>
            {copied && <span className="toast-note">Copied!</span>}
          </div>
        )}
      </div>
      <div className="toast-actions">
        {actions.map((action) => (
          <button key={action.label} className="button tertiary" type="button" onClick={action.onClick}>
            {action.label}
          </button>
        ))}
        <button className="button ghost" type="button" onClick={onClose} aria-label="Dismiss notification">
          ✕
        </button>
      </div>
    </div>
  )
}
