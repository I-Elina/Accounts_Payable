import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from './Button';

export function ErrorState({
  title = 'Failed to load data',
  message = 'An unexpected error occurred. Please try again.',
  error,
  onRetry,
}) {
  const errorMsg = error?.message || (typeof error === 'string' ? error : message);

  return (
    <div className="state-container" style={{ color: 'var(--color-exception)' }}>
      <AlertCircle size={48} />
      <div className="state-title" style={{ color: 'var(--color-exception)' }}>
        {title}
      </div>
      <p style={{ color: 'var(--color-text-muted)', maxWidth: 450 }}>{errorMsg}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry} icon={RotateCcw} style={{ marginTop: 'var(--space-3)' }}>
          Retry
        </Button>
      )}
    </div>
  );
}
