import React from 'react';
import { formatConfidence } from '../../lib/format';

export function ConfidenceBar({
  confidence,
  decision = 'needs_review',
  autoPassThreshold = 0.85,
  exceptionBelow = 0.40,
  showLabel = true,
}) {
  const score = Math.max(0, Math.min(1, Number(confidence) || 0));
  const percent = (score * 100).toFixed(1);

  // Decision-driven color class
  const decisionClass = decision || 'needs_review';

  return (
    <div className="confidence-bar-container">
      {showLabel && (
        <div className="confidence-bar-header">
          <span>Confidence</span>
          <span>{formatConfidence(score)}</span>
        </div>
      )}
      <div className="confidence-bar-track">
        <div
          className={`confidence-bar-fill ${decisionClass}`}
          style={{ width: `${percent}%` }}
        />
        {/* Threshold marks */}
        <div
          className="confidence-bar-threshold"
          style={{ left: `${autoPassThreshold * 100}%` }}
          title={`Auto-pass threshold: ${autoPassThreshold}`}
        />
        <div
          className="confidence-bar-threshold"
          style={{ left: `${exceptionBelow * 100}%` }}
          title={`Exception threshold: ${exceptionBelow}`}
        />
      </div>
    </div>
  );
}
