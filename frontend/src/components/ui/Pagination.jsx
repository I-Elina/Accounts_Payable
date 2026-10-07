import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export function Pagination({ page = 1, pageSize = 25, total = 0, onPageChange }) {
  const totalPages = Math.ceil(total / pageSize) || 1;
  const startRow = Math.min((page - 1) * pageSize + 1, total);
  const endRow = Math.min(page * pageSize, total);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--space-3) var(--space-4)',
        backgroundColor: 'var(--color-surface)',
        borderTop: '1px solid var(--color-border)',
        borderBottomLeftRadius: 'var(--radius)',
        borderBottomRightRadius: 'var(--radius)',
      }}
    >
      <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
        Showing {total > 0 ? `${startRow}–${endRow}` : '0'} of {total} invoices
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <Button
          variant="secondary"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          icon={ChevronLeft}
        >
          Previous
        </Button>
        <span style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, padding: '0 8px' }}>
          Page {page} of {totalPages}
        </span>
        <Button
          variant="secondary"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next
          <ChevronRight size={14} />
        </Button>
      </div>
    </div>
  );
}
