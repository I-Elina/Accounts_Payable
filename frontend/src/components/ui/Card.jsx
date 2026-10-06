import React from 'react';

export function Card({ title, action, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {title && (
        <div className="card-title">
          <span>{title}</span>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
