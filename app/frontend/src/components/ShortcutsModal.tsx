interface Shortcut {
  key: string
  description: string
}

interface ShortcutsModalProps {
  shortcuts: Shortcut[]
  onClose: () => void
}

export function ShortcutsModal({ shortcuts, onClose }: ShortcutsModalProps) {
  return (
    <div
      className="shortcuts-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
      onClick={onClose}
    >
      <div className="shortcuts-modal" onClick={(event) => event.stopPropagation()}>
        <header>
          <h3 id="shortcuts-title">Keyboard shortcuts</h3>
          <button className="button ghost" type="button" onClick={onClose} aria-label="Close shortcuts">
            ✕
          </button>
        </header>
        <ul>
          {shortcuts.map((shortcut) => (
            <li key={shortcut.key}>
              <code>{shortcut.key}</code>
              <span>{shortcut.description}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
