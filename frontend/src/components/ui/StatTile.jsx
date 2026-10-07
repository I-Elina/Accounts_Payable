import React from 'react';

export function StatTile({ label, value, subtext, icon: Icon, className = '' }) {
  return (
    <div className={`stat-tile ${className}`}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="stat-label">{label}</span>
        {Icon && <Icon size={18} style={{ color: 'var(--color-text-muted)' }} />}
      </div>
      <div className="stat-value">{value}</div>
      {subtext && <div className="stat-subtext">{subtext}</div>}
    </div>
  );
}
