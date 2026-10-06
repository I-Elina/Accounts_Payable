import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { Badge } from '../components/ui/Badge';
import { ConfidenceBar } from '../components/ui/ConfidenceBar';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { Toast } from '../components/ui/Toast';
import { InvoiceFields } from '../components/invoice/InvoiceFields';
import { MatchedCompare } from '../components/invoice/MatchedCompare';
import { ViolationsList } from '../components/invoice/ViolationsList';
import { ScoreBreakdown } from '../components/invoice/ScoreBreakdown';
import { AiSummaryCard } from '../components/invoice/AiSummaryCard';
import { ReviewActions } from '../components/invoice/ReviewActions';
import { ReviewHistory } from '../components/invoice/ReviewHistory';

export function InvoiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [toast, setToast] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  const fetchDetail = () => api.getInvoice(id);
  const { data, loading, error, refetch } = useApi(fetchDetail, [id]);

  // Auto-call createSummary if ai_summary_status === 'not_generated'
  useEffect(() => {
    if (data?.decision?.ai_summary_status === 'not_generated') {
      setAiLoading(true);
      api
        .createSummary(data.invoice.id || id)
        .then(() => refetch())
        .catch(() => {})
        .finally(() => setAiLoading(false));
    }
  }, [data?.decision?.ai_summary_status]);

  if (loading) return <Spinner label={`Loading invoice ${id} details...`} />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;
  if (!data || !data.invoice) return <ErrorState message="Invoice detail record not found" />;

  const { invoice, decision, matched_invoice, reviews } = data;

  const handleReviewExecute = async ({ action, reviewer, comment }) => {
    try {
      await api.reviewInvoice(invoice.id, { action, reviewer, comment });
      setToast({ message: `Successfully ${action}d invoice ${invoice.invoice_id}`, type: 'success' });
      refetch();
    } catch (err) {
      setToast({ message: err.message || 'Failed to submit review', type: 'error' });
      throw err;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      {/* Top Navigation & Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Button variant="secondary" size="sm" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Back
        </Button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <span className="font-mono" style={{ fontSize: 'var(--fs-xl)', fontWeight: 700 }}>
            {invoice.invoice_id}
          </span>
          <Badge type="decision" value={decision.decision} />
          <Badge type="review_status" value={decision.review_status} />
        </div>
      </div>

      {/* Confidence Score Bar */}
      <div className="card">
        <ConfidenceBar confidence={decision.confidence} decision={decision.decision} showLabel={true} />
      </div>

      {/* Main Grid: Left Fields, Right Matched Compare */}
      <div style={{ display: 'grid', gridTemplateColumns: matched_invoice ? '1fr 1fr' : '1fr', gap: 'var(--space-4)' }}>
        <InvoiceFields invoice={invoice} />
        {matched_invoice && <MatchedCompare invoice={invoice} matchedInvoice={matched_invoice} />}
      </div>

      {/* Decision Engine Score Breakdown */}
      <ScoreBreakdown decision={decision} />

      {/* Violations List */}
      <ViolationsList violations={decision.violations} />

      {/* AI Explanation Card */}
      <AiSummaryCard decision={decision} loading={aiLoading} />

      {/* Human Review Actions */}
      <ReviewActions
        invoiceId={invoice.invoice_id}
        reviewStatus={decision.review_status}
        onReview={handleReviewExecute}
      />

      {/* Review Audit History */}
      <ReviewHistory reviews={reviews} />

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
