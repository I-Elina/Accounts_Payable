import React from 'react';
import { Inbox } from 'lucide-react';
import { Button } from './Button';

export function EmptyState({
  title = 'No items found',
  message = 'Upload an invoice file to get started.',
  actionLabel,
  onAction,
  icon: Icon = Inbox,
}) {
  return (
    <div className="state-container">
      <Icon size={48} style={{ color: 'var(--color-text-muted)', opacity: 0.6 }} />
      <div className="state-title">{title}</div>
      <p style={{ color: 'var(--color-text-muted)', maxWidth: 400 }}>{message}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} style={{ marginTop: 'var(--space-3)' }}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
