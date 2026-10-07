import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, CheckCircle2, XCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { ConfidenceBar } from '../ui/ConfidenceBar';
import { Button } from '../ui/Button';
import { formatMoney } from '../../lib/format';
import { useReviewer } from '../../hooks/useReviewer';

export function ExceptionCard({ card, onReviewSuccess }) {
  const navigate = useNavigate();
  const [reviewer] = useReviewer();
  const [confirmAction, setConfirmAction] = useState(null); // 'approve' | 'reject' | null
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const isPending = card.review_status === 'pending';
  const isReviewerValid = Boolean(reviewer && reviewer.trim());

  const handleReviewExecute = async () => {
    if (!confirmAction || !isReviewerValid || submitting) return;
    setSubmitting(true);
    try {
      if (onReviewSuccess) {
        await onReviewSuccess(card.id || card.invoice_id, confirmAction, reviewer, comment);
      }
      setConfirmAction(null);
      setComment('');
    } catch (e) {
      // Handled by parent
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="chat-exception-card">
      <div className="chat-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span className="chat-card-title">{card.invoice_id}</span>
          <Badge type="decision" value={card.decision} />
        </div>
        <div style={{ fontWeight: 700, fontSize: 'var(--fs-sm)' }}>
          {formatMoney(card.total_amount, card.currency)}
        </div>
      </div>

      <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text)' }}>
        <strong>Vendor:</strong> {card.vendor_name}
      </div>

      <ConfidenceBar confidence={card.confidence} decision={card.decision} showLabel={true} />

      {card.primary_reason && (
        <div className="chat-card-reason">
          {card.primary_reason}
        </div>
      )}

      {card.matched_record && (
        <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-primary)' }}>
          Matched Record:{' '}
          <button
            onClick={() => navigate(`/invoices?search=${card.matched_record}`)}
            style={{ fontWeight: 600, textDecoration: 'underline' }}
          >
            {card.matched_record}
          </button>
        </div>
      )}

      <div className="chat-card-actions">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/invoices/${card.id || card.invoice_id}`)}
          icon={ExternalLink}
        >
          Open details
        </Button>

        {isPending && (
          <>
            <Button
              variant="danger"
              size="sm"
              disabled={!isReviewerValid}
              onClick={() => setConfirmAction('reject')}
              icon={XCircle}
            >
              Reject
            </Button>
            <Button
              variant="pass"
              size="sm"
              disabled={!isReviewerValid}
              onClick={() => setConfirmAction('approve')}
              icon={CheckCircle2}
            >
              Approve
            </Button>
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmAction && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-title">
              Confirm {confirmAction === 'approve' ? 'Approval' : 'Rejection'}
            </div>
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-text-muted)' }}>
              Are you sure you want to <strong>{confirmAction.toUpperCase()}</strong> invoice{' '}
              <strong className="font-mono">{card.invoice_id}</strong> as reviewer <strong>{reviewer}</strong>?
            </p>

            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Optional comment..."
              rows={2}
              className="filter-input"
              style={{ width: '100%' }}
            />

            <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end' }}>
              <Button variant="secondary" onClick={() => setConfirmAction(null)} disabled={submitting}>
                Cancel
              </Button>
              <Button
                variant={confirmAction === 'approve' ? 'pass' : 'danger'}
                onClick={handleReviewExecute}
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
