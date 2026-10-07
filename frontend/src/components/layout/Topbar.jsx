import React from 'react';
import { User, ShieldCheck } from 'lucide-react';
import { useReviewer } from '../../hooks/useReviewer';

export function Topbar({ pageTitle, autoPassThreshold = 0.85 }) {
  const [reviewer, setReviewer] = useReviewer();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="topbar-page-title">{pageTitle}</h1>
      </div>

      <div className="topbar-right">
        {/* Threshold Badge */}
        <div className="threshold-badge" title="Current auto-pass threshold set in Settings">
          <ShieldCheck size={14} />
          <span>Auto-pass: {Number(autoPassThreshold).toFixed(2)}</span>
        </div>

        {/* Reviewer Name Input */}
        <div className="reviewer-field">
          <User size={14} style={{ color: 'var(--color-text-muted)' }} />
          <span className="reviewer-label">Reviewer:</span>
          <input
            type="text"
            className="reviewer-input"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="Your Name"
            title="Reviewer name stored for audit events"
          />
        </div>
      </div>
    </header>
  );
}
