import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { FilterBar } from '../components/ui/FilterBar';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { ConfidenceBar } from '../components/ui/ConfidenceBar';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Pagination } from '../components/ui/Pagination';
import { formatMoney, formatDate } from '../lib/format';

export function Invoices() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    search: '',
    decision: '',
    exception_type: '',
    review_status: '',
    category: '',
    sort: 'invoice_id',
    order: 'asc',
  });
  const [page, setPage] = useState(1);

  const fetchInvoices = () =>
    api.getInvoices({
      ...filters,
      page,
      page_size: 25,
    });

  const { data, loading, error, refetch } = useApi(fetchInvoices, [filters, page]);

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
      header: 'Category',
      key: 'category',
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Invoices Master Directory</h2>
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
            Search, filter, and inspect all invoices processed across batches.
          </span>
        </div>

        <Button variant="secondary" icon={Download} onClick={handleDownloadReport}>
          Download Report (CSV)
        </Button>
      </div>

      <FilterBar
        filters={filters}
        onChange={(newFilters) => {
          setFilters(newFilters);
          setPage(1);
        }}
        onReset={() => {
          setFilters({ search: '', decision: '', exception_type: '', review_status: '', category: '', sort: 'invoice_id', order: 'asc' });
          setPage(1);
        }}
      />

      {loading && <Spinner label="Loading invoices..." />}

      {error && <ErrorState error={error} onRetry={refetch} />}

      {!loading && !error && data?.items?.length === 0 && (
        <EmptyState
          title="No invoices matched your filters"
          message="Try adjusting your filter search criteria or upload a new file."
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
