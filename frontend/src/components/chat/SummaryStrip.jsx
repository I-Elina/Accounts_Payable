import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import { Button } from '../ui/Button';

export function SummaryStrip({ stats, onDownloadReport }) {
  const navigate = useNavigate();

  if (!stats) return null;

  const total = stats.total || 0;
  const autoPass = stats.by_decision?.auto_pass || 0;
  const needsReview = stats.by_decision?.needs_review || 0;
  const exception = stats.by_decision?.exception || 0;
  const pending = stats.pending_reviews || 0;

  return (
    <div className="summary-strip">
      <div className="summary-strip-item">
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>Batch Total:</span>
        <span className="summary-strip-value">{total}</span>
      </div>

      <div className="summary-strip-item">
        <CheckCircle2 size={16} color="var(--color-pass)" />
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>Auto-passed:</span>
        <span className="summary-strip-value" style={{ color: 'var(--color-pass)' }}>{autoPass}</span>
      </div>

      <div className="summary-strip-item">
        <AlertTriangle size={16} color="var(--color-review)" />
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>Needs Review:</span>
        <span className="summary-strip-value" style={{ color: 'var(--color-review)' }}>{needsReview}</span>
      </div>

      <div className="summary-strip-item">
        <XCircle size={16} color="var(--color-exception)" />
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>Exceptions:</span>
        <span className="summary-strip-value" style={{ color: 'var(--color-exception)' }}>{exception}</span>
      </div>

      <div className="summary-strip-item">
        <Clock size={16} color="var(--color-primary)" />
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--fs-xs)' }}>Pending:</span>
        <span className="summary-strip-value" style={{ color: 'var(--color-primary)' }}>{pending}</span>
      </div>

      <div style={{ display: 'flex', gap: 'var(--space-2)', marginLeft: 'auto' }}>
        <Button variant="secondary" size="sm" onClick={() => navigate('/queue')}>
          View Review Queue
        </Button>
        {onDownloadReport && (
          <Button variant="primary" size="sm" onClick={onDownloadReport}>
            Download Report (CSV)
          </Button>
        )}
      </div>
    </div>
  );
}
