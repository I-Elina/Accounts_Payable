import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, Filter } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { ConfidenceBar } from '../components/ui/ConfidenceBar';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Pagination } from '../components/ui/Pagination';
import { formatMoney, formatDate } from '../lib/format';
import { EXCEPTION_TYPES } from '../lib/constants';
import { EXCEPTION_LABEL } from '../lib/labels';

export function ReviewQueue() {
  const navigate = useNavigate();
  const [selectedType, setSelectedType] = useState('');
  const [page, setPage] = useState(1);

  const fetchQueue = () =>
    api.getInvoices({
      review_status: 'pending',
      decision: 'needs_review,exception',
      exception_type: selectedType || undefined,
      sort: 'confidence',
      order: 'asc',
      page,
      page_size: 25,
    });

  const { data, loading, error, refetch } = useApi(fetchQueue, [selectedType, page]);

  const columns = [
    {
      header: 'Invoice ID',
      key: 'invoice_id',
      render: (val) => <span className="font-mono" style={{ fontWeight: 600 }}>{val}</span>,
    },
    {
      header: 'Vendor Name',
      key: 'vendor_name',
      render: (val) => <strong>{val}</strong>,
    },
    {
      header: 'Invoice Date',
      key: 'invoice_date',
      render: (val) => formatDate(val),
    },
    {
      header: 'Amount',
      key: 'total_amount',
      render: (val, row) => formatMoney(val, row.currency),
    },
    {
      header: 'Decision',
      key: 'decision',
      render: (val) => <Badge type="decision" value={val} />,
    },
    {
      header: 'Confidence',
      key: 'confidence',
      width: 140,
      render: (val, row) => <ConfidenceBar confidence={val} decision={row.decision} showLabel={false} />,
    },
    {
      header: 'Exception Type',
      key: 'exception_type',
      render: (val) => <Badge type="exception_type" value={val} />,
    },
    {
      header: 'Review Status',
      key: 'review_status',
      render: (val) => <Badge type="review_status" value={val} />,
    },
  ];

  const handleDownloadReport = () => {
    const url = api.reportUrl(1);
    window.open(url, '_blank');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Pending Review Queue</h2>
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
            Lowest confidence scores listed first. Select an invoice to review details and approve/reject.
          </span>
        </div>

        <Button variant="secondary" icon={Download} onClick={handleDownloadReport}>
          Download Report (CSV)
        </Button>
      </div>

      {/* Exception Type Filter Tabs */}
      <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-2)' }}>
        <button
          onClick={() => { setSelectedType(''); setPage(1); }}
          className={`btn ${selectedType === '' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
        >
          All Exceptions
        </button>
        {EXCEPTION_TYPES.filter((t) => t !== 'none').map((type) => (
          <button
            key={type}
            onClick={() => { setSelectedType(type); setPage(1); }}
            className={`btn ${selectedType === type ? 'btn-primary' : 'btn-secondary'} btn-sm`}
          >
            {EXCEPTION_LABEL[type] || type}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading && <Spinner label="Loading pending review queue..." />}

      {error && <ErrorState error={error} onRetry={refetch} />}

      {!loading && !error && data?.items?.length === 0 && (
        <EmptyState
          title="No pending reviews"
          message="All exception pile invoices have been reviewed! Upload a new batch to continue."
          actionLabel="Go to Upload"
          onAction={() => navigate('/upload')}
        />
      )}

      {!loading && !error && data?.items?.length > 0 && (
        <div>
          <DataTable
            columns={columns}
            data={data.items}
            onRowClick={(row) => navigate(`/invoices/${row.id}`)}
          />
          <Pagination
            page={data.page}
            pageSize={data.page_size}
            total={data.total}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}
    </div>
  );
}
