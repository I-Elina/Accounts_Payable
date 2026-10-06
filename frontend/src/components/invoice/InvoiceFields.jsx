import React from 'react';
import { formatMoney, formatDate } from '../../lib/format';

export function InvoiceFields({ invoice, className = '' }) {
  if (!invoice) return null;

  const fields = [
    { label: 'Invoice ID', value: <span className="font-mono">{invoice.invoice_id}</span> },
    { label: 'Invoice Number', value: <span className="font-mono">{invoice.invoice_number || '—'}</span> },
    { label: 'Vendor Name', value: <strong>{invoice.vendor_name}</strong> },
    { label: 'Invoice Date', value: formatDate(invoice.invoice_date) },
    { label: 'Due Date', value: formatDate(invoice.due_date) },
    { label: 'Category', value: invoice.category || '—' },
    { label: 'PO Number', value: invoice.po_number ? <span className="font-mono">{invoice.po_number}</span> : '—' },
    { label: 'Subtotal', value: formatMoney(invoice.subtotal, invoice.currency) },
    { label: 'Tax Amount', value: formatMoney(invoice.tax_amount, invoice.currency) },
    { label: 'Total Amount', value: <strong style={{ fontSize: 'var(--fs-md)' }}>{formatMoney(invoice.total_amount, invoice.currency)}</strong> },
    { label: 'Description', value: invoice.description || '—', fullWidth: true },
  ];

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Invoice Details</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
        {fields.map((f, idx) => (
          <div
            key={idx}
            style={{
              gridColumn: f.fullWidth ? '1 / -1' : 'span 1',
              padding: 'var(--space-2) 0',
              borderBottom: '1px solid var(--color-border)',
            }}
          >
            <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', fontWeight: 600 }}>
              {f.label}
            </div>
            <div style={{ fontSize: 'var(--fs-sm)', marginTop: 2 }}>{f.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
