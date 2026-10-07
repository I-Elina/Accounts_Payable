import React from 'react';
import { AlertCircle } from 'lucide-react';

export function ViolationsList({ violations = [], className = '' }) {
  if (!violations || violations.length === 0) {
    return (
      <div className={`card ${className}`}>
        <div className="card-title">Rule Violations</div>
        <p style={{ color: 'var(--color-pass)', fontSize: 'var(--fs-sm)' }}>
          ✓ Clean invoice. No rule violations triggered during engine evaluation.
        </p>
      </div>
    );
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Triggered Rule Violations ({violations.length})</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {violations.map((v, idx) => (
          <div
            key={idx}
            style={{
              backgroundColor: 'var(--color-bg)',
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius)',
              borderLeft: `4px solid ${v.severity === 'hard' ? 'var(--color-exception)' : 'var(--color-review)'}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span className="font-mono" style={{ fontWeight: 700, color: 'var(--color-text)' }}>
                  [{v.rule_id}] {v.name}
                </span>
                <span
                  style={{
                    fontSize: 'var(--fs-xs)',
                    padding: '2px 6px',
                    borderRadius: 4,
                    backgroundColor: v.severity === 'hard' ? 'var(--color-exception-bg)' : 'var(--color-review-bg)',
                    color: v.severity === 'hard' ? 'var(--color-exception)' : 'var(--color-review)',
                    fontWeight: 600,
                  }}
                >
                  {v.severity.toUpperCase()}
                </span>
              </div>
              <span className="penalty-tag" style={{ fontSize: 'var(--fs-xs)' }}>
                Penalty: -{v.penalty}
              </span>
            </div>

            <p style={{ marginTop: 'var(--space-2)', fontSize: 'var(--fs-sm)', color: 'var(--color-text)' }}>
              {v.message}
            </p>

            {v.evidence && Object.keys(v.evidence).length > 0 && (
              <div
                style={{
                  marginTop: 'var(--space-2)',
                  fontSize: 'var(--fs-xs)',
                  fontFamily: 'var(--font-mono)',
                  backgroundColor: 'var(--color-surface)',
                  padding: 'var(--space-2)',
                  borderRadius: 4,
                  border: '1px solid var(--color-border)',
                }}
              >
                <strong>Evidence:</strong>
                {Object.entries(v.evidence).map(([ekey, evalue]) => (
                  <div key={ekey} style={{ marginLeft: 8 }}>
                    • {ekey}: {typeof evalue === 'number' ? evalue.toFixed(2) : String(evalue)}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
