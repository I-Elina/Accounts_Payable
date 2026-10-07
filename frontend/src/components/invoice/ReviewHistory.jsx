import React from 'react';
import { User, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { formatDateTime } from '../../lib/format';

export function ReviewHistory({ reviews = [], className = '' }) {
  if (!reviews || reviews.length === 0) {
    return null;
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Review Audit History</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {reviews.map((r, idx) => {
          const isApproved = r.action === 'approve';
          return (
            <div
              key={r.id || idx}
              style={{
                backgroundColor: 'var(--color-bg)',
                padding: 'var(--space-3)',
                borderRadius: 'var(--radius)',
                borderLeft: `4px solid ${isApproved ? 'var(--color-pass)' : 'var(--color-exception)'}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  {isApproved ? (
                    <CheckCircle2 size={16} color="var(--color-pass)" />
                  ) : (
                    <XCircle size={16} color="var(--color-exception)" />
                  )}
                  <span style={{ fontWeight: 700, textTransform: 'capitalize' }}>{r.action}d</span>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>by</span>
                  <span style={{ fontWeight: 600 }}>{r.reviewer}</span>
                </div>
                <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
                  {formatDateTime(r.reviewed_at)}
                </span>
              </div>

              {r.comment && (
                <div style={{ marginTop: 'var(--space-2)', fontSize: 'var(--fs-xs)', color: 'var(--color-text)' }}>
                  "{r.comment}"
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
