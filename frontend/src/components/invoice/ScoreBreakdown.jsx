import React from 'react';
import { formatConfidence } from '../../lib/format';
import { Badge } from '../ui/Badge';

export function ScoreBreakdown({ decision, className = '' }) {
  if (!decision) return null;

  const violations = decision.violations || [];
  const baseScore = 1.00;

  return (
    <div className={`score-breakdown ${className}`}>
      <div className="card-title">
        <span>Decision Score Breakdown</span>
        <Badge type="decision" value={decision.decision} />
      </div>

      <div className="breakdown-row">
        <span>Base Starting Score</span>
        <span className="font-mono" style={{ fontWeight: 600 }}>1.00</span>
      </div>

      {violations.map((v, idx) => (
        <div key={idx} className="breakdown-row">
          <div>
            <span className="font-mono" style={{ fontWeight: 600, marginRight: 8, color: 'var(--color-primary)' }}>
              {v.rule_id}
            </span>
            <span>{v.name || v.message}</span>
            <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', marginLeft: 6 }}>
              ({v.severity} rule)
            </span>
          </div>
          <span className="penalty-tag">−{Number(v.penalty).toFixed(2)}</span>
        </div>
      ))}

      {violations.length === 0 && (
        <div className="breakdown-row" style={{ color: 'var(--color-pass)' }}>
          <span>No rule violations detected</span>
          <span className="font-mono">0.00</span>
        </div>
      )}

      <div className="breakdown-row total">
        <span>Final Confidence Score</span>
        <span className="font-mono">{formatConfidence(decision.confidence)}</span>
      </div>
    </div>
  );
}
