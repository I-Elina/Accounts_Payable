import React from 'react';

export function Spinner({ size = 32, label = 'Loading...' }) {
  return (
    <div className="state-container" style={{ minHeight: 180 }}>
      <div className="spinner" style={{ width: size, height: size }} />
      {label && <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>{label}</span>}
    </div>
  );
}
