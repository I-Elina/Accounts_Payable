import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, ShieldCheck, ShieldAlert } from 'lucide-react';
import { DECISION_LABEL, REVIEW_STATUS_LABEL, EXCEPTION_LABEL } from '../../lib/labels';

export function Badge({ type = 'decision', value, className = '' }) {
  if (!value) return null;

  if (type === 'decision') {
    const label = DECISION_LABEL[value] || value;
    let icon = null;
    if (value === 'auto_pass') icon = <CheckCircle2 size={12} />;
    else if (value === 'needs_review') icon = <AlertTriangle size={12} />;
    else if (value === 'exception') icon = <XCircle size={12} />;

    return (
      <span className={`badge badge-${value} ${className}`}>
        {icon}
        {label}
      </span>
    );
  }

  if (type === 'review_status') {
    const label = REVIEW_STATUS_LABEL[value] || value;
    let icon = <Clock size={12} />;
    if (value === 'approved') icon = <ShieldCheck size={12} />;
    if (value === 'rejected') icon = <ShieldAlert size={12} />;

    return (
      <span className={`badge badge-neutral ${className}`}>
        {icon}
        {label}
      </span>
    );
  }

  if (type === 'exception_type') {
    const label = EXCEPTION_LABEL[value] || value;
    return (
      <span className={`badge badge-neutral ${className}`}>
        {label}
      </span>
    );
  }

  return <span className={`badge badge-neutral ${className}`}>{value}</span>;
}
