import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, X } from 'lucide-react';

export function Toast({ message, type = 'info', onClose }) {
  if (!message) return null;

  let icon = <CheckCircle2 size={18} color="var(--color-pass)" />;
  if (type === 'error') icon = <XCircle size={18} color="var(--color-exception)" />;
  if (type === 'warning') icon = <AlertTriangle size={18} color="var(--color-review)" />;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        boxShadow: '0 4px 14px rgba(17,33,63,0.12)',
        borderRadius: 'var(--radius)',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        zIndex: 2000,
        maxWidth: 360,
      }}
    >
      {icon}
      <span style={{ fontSize: 'var(--fs-sm)', flex: 1, color: 'var(--color-text)' }}>{message}</span>
      {onClose && (
        <button onClick={onClose} style={{ cursor: 'pointer', color: 'var(--color-text-muted)' }}>
          <X size={14} />
        </button>
      )}
    </div>
  );
}
