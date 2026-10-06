import React, { useState } from 'react';
import { Sparkles, CheckCircle2, XCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { useReviewer } from '../../hooks/useReviewer';

export function ProposalConfirm({ proposal, onConfirm, onDismiss }) {
  const [reviewer] = useReviewer();
  const [submitting, setSubmitting] = useState(false);

  if (!proposal) return null;

  const isApproved = proposal.action === 'approve';
  const isReviewerValid = Boolean(reviewer && reviewer.trim());

  const handleConfirm = async () => {
    if (!isReviewerValid || submitting) return;
    setSubmitting(true);
    try {
      await onConfirm(proposal, reviewer);
    } catch (e) {
      // error handled by parent
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="proposal-bar">
      <div className="proposal-info">
        <Sparkles size={16} />
        <div>
          Assistant proposes to <strong>{proposal.action.toUpperCase()}</strong> invoice{' '}
          <strong className="font-mono">{proposal.invoice_id}</strong>
          {proposal.reason && <div style={{ fontSize: 'var(--fs-xs)', fontWeight: 400 }}>"{proposal.reason}"</div>}
        </div>
      </div>

      <div className="proposal-actions">
        {!isReviewerValid ? (
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-review)', alignSelf: 'center' }}>
            Set reviewer name in topbar
          </span>
        ) : (
          <Button
            variant={isApproved ? 'pass' : 'danger'}
            size="sm"
            onClick={handleConfirm}
            disabled={submitting}
          >
            {submitting ? 'Executing...' : `Confirm ${proposal.action}`}
          </Button>
        )}

        <Button variant="secondary" size="sm" onClick={onDismiss} disabled={submitting}>
          Dismiss
        </Button>
      </div>
    </div>
  );
}
