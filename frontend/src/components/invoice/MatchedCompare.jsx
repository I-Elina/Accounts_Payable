import React from 'react';
import { formatMoney, formatDate } from '../../lib/format';

export function MatchedCompare({ invoice, matchedInvoice, className = '' }) {
  if (!matchedInvoice) return null;

  const compareRows = [
    { label: 'Invoice ID', current: invoice.invoice_id, matched: matchedInvoice.invoice_id, isMono: true },
    { label: 'Invoice Number', current: invoice.invoice_number, matched: matchedInvoice.invoice_number, isMono: true },
    { label: 'Vendor Name', current: invoice.vendor_name, matched: matchedInvoice.vendor_name },
    { label: 'Invoice Date', current: formatDate(invoice.invoice_date), matched: formatDate(matchedInvoice.invoice_date) },
    { label: 'Total Amount', current: formatMoney(invoice.total_amount, invoice.currency), matched: formatMoney(matchedInvoice.total_amount, matchedInvoice.currency) },
    { label: 'Category', current: invoice.category, matched: matchedInvoice.category },
    { label: 'PO Number', current: invoice.po_number || '—', matched: matchedInvoice.po_number || '—', isMono: true },
  ];

  return (
    <div className={`card ${className}`}>
      <div className="card-title" style={{ color: 'var(--color-review)' }}>
        Side-by-Side Comparison: Current vs Matched Record ({matchedInvoice.invoice_id})
      </div>

      <div className="matched-compare-grid">
        {/* Column 1: Current Invoice */}
        <div style={{ backgroundColor: 'var(--color-bg)', padding: 'var(--space-3)', borderRadius: 'var(--radius)' }}>
          <div style={{ fontWeight: 700, marginBottom: 'var(--space-2)', color: 'var(--color-primary)' }}>
            Current: {invoice.invoice_id}
          </div>
          {compareRows.map((row, idx) => {
            const isDifferent = String(row.current) !== String(row.matched);
            return (
              <div
                key={idx}
                style={{
                  padding: '4px 0',
                  borderBottom: '1px solid var(--color-border)',
                  fontSize: 'var(--fs-xs)',
                }}
              >
                <span style={{ color: 'var(--color-text-muted)', display: 'block' }}>{row.label}</span>
                <span
                  className={`${row.isMono ? 'font-mono' : ''} ${isDifferent ? 'diff-field-highlight' : ''}`}
                >
                  {row.current}
                </span>
              </div>
            );
          })}
        </div>

        {/* Column 2: Matched Invoice */}
        <div style={{ backgroundColor: 'var(--color-bg)', padding: 'var(--space-3)', borderRadius: 'var(--radius)' }}>
          <div style={{ fontWeight: 700, marginBottom: 'var(--space-2)', color: 'var(--color-text-muted)' }}>
            Matched: {matchedInvoice.invoice_id}
          </div>
          {compareRows.map((row, idx) => {
            const isDifferent = String(row.current) !== String(row.matched);
            return (
              <div
                key={idx}
                style={{
                  padding: '4px 0',
                  borderBottom: '1px solid var(--color-border)',
                  fontSize: 'var(--fs-xs)',
                }}
              >
                <span style={{ color: 'var(--color-text-muted)', display: 'block' }}>{row.label}</span>
                <span
                  className={`${row.isMono ? 'font-mono' : ''} ${isDifferent ? 'diff-field-highlight' : ''}`}
                >
                  {row.matched}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
