import React from 'react';
import { Download, CheckCircle2, AlertTriangle, XCircle, BarChart3 } from 'lucide-react';
import { ExceptionCard } from './ExceptionCard';
import { StatTile } from '../ui/StatTile';
import { Button } from '../ui/Button';

export function CardRenderer({ card, onReviewSuccess }) {
  if (!card) return null;

  if (card.type === 'invoice') {
    return <ExceptionCard card={card} onReviewSuccess={onReviewSuccess} />;
  }

  if (card.type === 'stats') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 'var(--space-3)', margin: 'var(--space-2) 0' }}>
        <StatTile label="Total Rows" value={card.total} icon={BarChart3} />
        <StatTile label="Auto-passed" value={card.auto_pass} icon={CheckCircle2} />
        <StatTile label="Needs Review" value={card.needs_review} icon={AlertTriangle} />
        <StatTile label="Exceptions" value={card.exception} icon={XCircle} />
      </div>
    );
  }

  if (card.type === 'report') {
    return (
      <div
        style={{
          backgroundColor: 'var(--color-primary-soft)',
          border: '1px solid var(--color-primary)',
          borderRadius: 'var(--radius)',
          padding: 'var(--space-3) var(--space-4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-3)',
          margin: 'var(--space-2) 0',
        }}
      >
        <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 600, color: 'var(--color-primary)' }}>
          AP Exception Pile Report (CSV Download)
        </div>
        <a href={card.url} download="ap_exception_report.csv" style={{ textDecoration: 'none' }}>
          <Button variant="primary" size="sm" icon={Download}>
            Download Report CSV
          </Button>
        </a>
      </div>
    );
  }

  return null;
}
