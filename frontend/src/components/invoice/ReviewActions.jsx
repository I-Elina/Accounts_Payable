import React, { useState } from 'react';
import { CheckCircle2, XCircle, ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';
import { useReviewer } from '../../hooks/useReviewer';

export function ReviewActions({ invoiceId, reviewStatus = 'pending', onReview, className = '' }) {
  const [reviewer] = useReviewer();
  const [comment, setComment] = useState('');
  const [confirmAction, setConfirmAction] = useState(null); // 'approve' | 'reject' | null
  const [submitting, setSubmitting] = useState(false);

  if (reviewStatus !== 'pending') {
    return (
      <div className={`card ${className}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <ShieldAlert size={18} style={{ color: 'var(--color-text-muted)' }} />
          <span style={{ fontWeight: 600 }}>Review completed. Status: {reviewStatus.toUpperCase()}</span>
        </div>
      </div>
    );
  }

  const isReviewerValid = Boolean(reviewer && reviewer.trim());

  const handleExecute = async () => {
    if (!confirmAction || !isReviewerValid) return;
    setSubmitting(true);
    try {
      await onReview({ action: confirmAction, reviewer, comment });
      setConfirmAction(null);
      setComment('');
    } catch (e) {
      // Handled by parent toast/error
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Human Review Action</div>

      {!isReviewerValid && (
        <div
          style={{
            fontSize: 'var(--fs-xs)',
            color: 'var(--color-review)',
            backgroundColor: 'var(--color-review-bg)',
            padding: 'var(--space-2) var(--space-3)',
            borderRadius: 'var(--radius)',
            marginBottom: 'var(--space-3)',
          }}
        >
          ⚠️ Please enter your Reviewer Name in the topbar before approving or rejecting.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        <div>
          <label style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>
            Review Comment (optional)
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add justification or notes for audit trail..."
            rows={2}
            className="filter-input"
            style={{ width: '100%', resize: 'vertical' }}
          />
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end' }}>
          <Button
            variant="danger"
            icon={XCircle}
            disabled={!isReviewerValid || submitting}
            onClick={() => setConfirmAction('reject')}
          >
            Reject
          </Button>

          <Button
            variant="pass"
            icon={CheckCircle2}
            disabled={!isReviewerValid || submitting}
            onClick={() => setConfirmAction('approve')}
          >
            Approve
          </Button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmAction && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-title">
              Confirm Invoice {confirmAction === 'approve' ? 'Approval' : 'Rejection'}
            </div>
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-text-muted)' }}>
              Are you sure you want to <strong>{confirmAction.toUpperCase()}</strong> invoice{' '}
              <strong className="font-mono">{invoiceId}</strong> as reviewer <strong>{reviewer}</strong>?
            </p>
            {comment && (
              <div style={{ fontSize: 'var(--fs-xs)', backgroundColor: 'var(--color-bg)', padding: 'var(--space-2)', borderRadius: 4 }}>
                <strong>Comment:</strong> "{comment}"
              </div>
            )}
            <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end', marginTop: 'var(--space-2)' }}>
              <Button variant="secondary" onClick={() => setConfirmAction(null)} disabled={submitting}>
                Cancel
              </Button>
              <Button
                variant={confirmAction === 'approve' ? 'pass' : 'danger'}
                onClick={handleExecute}
                disabled={submitting}
              >
                {submitting ? 'Executing...' : `Confirm ${confirmAction === 'approve' ? 'Approve' : 'Reject'}`}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
