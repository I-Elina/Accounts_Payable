import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, User, Bot, Cpu, Settings as SettingsIcon, Search } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { DataTable } from '../components/ui/DataTable';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Pagination } from '../components/ui/Pagination';
import { formatDateTime } from '../lib/format';
import { EVENT_LABEL } from '../lib/labels';

export function AuditLog() {
  const navigate = useNavigate();
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [invoiceIdSearch, setInvoiceIdSearch] = useState('');
  const [page, setPage] = useState(1);
  const [expandedRowId, setExpandedRowId] = useState(null);

  const fetchAudit = () =>
    api.getAudit({
      event_type: eventTypeFilter || undefined,
      invoice_id: invoiceIdSearch || undefined,
      page,
      page_size: 25,
    });

  const { data, loading, error, refetch } = useApi(fetchAudit, [eventTypeFilter, invoiceIdSearch, page]);

  const renderActorIcon = (actorType) => {
    if (actorType === 'user') return <User size={14} color="var(--color-primary)" />;
    if (actorType === 'ai') return <Bot size={14} color="#7C3AED" />;
    if (actorType === 'engine') return <Cpu size={14} color="#D97706" />;
    return <SettingsIcon size={14} color="var(--color-text-muted)" />;
  };

  const columns = [
    {
      header: 'Timestamp (UTC)',
      key: 'timestamp',
      render: (val) => <span className="font-mono">{formatDateTime(val)}</span>,
    },
    {
      header: 'Actor',
      key: 'actor',
      render: (val, row) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {renderActorIcon(row.actor_type)}
          <strong>{val}</strong>
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>({row.actor_type})</span>
        </div>
      ),
    },
    {
      header: 'Event',
      key: 'event_type',
      render: (val) => (
        <span style={{ fontWeight: 600, color: 'var(--color-text)' }}>
          {EVENT_LABEL[val] || val}
        </span>
      ),
    },
    {
      header: 'Invoice ID',
      key: 'invoice_id',
      render: (val) =>
        val ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/invoices?search=${val}`);
            }}
            className="font-mono"
            style={{ color: 'var(--color-primary)', fontWeight: 600, textDecoration: 'underline' }}
          >
            {val}
          </button>
        ) : (
          '—'
        ),
    },
    {
      header: 'Details JSON',
      key: 'details',
      render: (val, row) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setExpandedRowId(expandedRowId === row.id ? null : row.id);
          }}
          className="btn btn-secondary btn-sm"
        >
          {expandedRowId === row.id ? 'Hide Details' : 'View Payload'}
        </button>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <div>
        <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Audit Trail Log</h2>
        <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
          Immutable, audit-ready record of every engine decision, AI explanation, user review, and system event.
        </span>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 10, color: 'var(--color-text-muted)' }} />
          <input
            type="text"
            placeholder="Filter by Invoice ID..."
            value={invoiceIdSearch}
            onChange={(e) => {
              setInvoiceIdSearch(e.target.value);
              setPage(1);
            }}
            className="filter-input"
            style={{ paddingLeft: 32 }}
          />
        </div>

        <select
          value={eventTypeFilter}
          onChange={(e) => {
            setEventTypeFilter(e.target.value);
            setPage(1);
          }}
          className="filter-input"
        >
          <option value="">All Event Types</option>
          {Object.entries(EVENT_LABEL).map(([typeKey, labelText]) => (
            <option key={typeKey} value={typeKey}>
              {labelText}
            </option>
          ))}
        </select>
      </div>

      {loading && <Spinner label="Loading audit logs..." />}
      {error && <ErrorState error={error} onRetry={refetch} />}

      {!loading && !error && data?.items?.length === 0 && (
        <EmptyState title="No audit events found" message="No audit logs matched your query filter." />
      )}

      {!loading && !error && data?.items?.length > 0 && (
        <div>
          <DataTable columns={columns} data={data.items} />

          {/* Expanded Details View Modal or Drawer */}
          {expandedRowId && (
            <div
              style={{
                backgroundColor: 'var(--color-navy)',
                color: 'var(--color-on-dark)',
                padding: 'var(--space-4)',
                borderRadius: 'var(--radius)',
                marginTop: 'var(--space-3)',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--fs-xs)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <strong>Details Payload (Event #{expandedRowId}):</strong>
                <button
                  onClick={() => setExpandedRowId(null)}
                  style={{ color: '#8A9DBB', cursor: 'pointer' }}
                >
                  Close [×]
                </button>
              </div>
              <pre style={{ whiteSpace: 'pre-wrap', overflowX: 'auto' }}>
                {JSON.stringify(
                  data.items.find((i) => i.id === expandedRowId)?.details,
                  null,
                  2
                )}
              </pre>
            </div>
          )}

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
