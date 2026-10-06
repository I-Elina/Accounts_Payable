import React from 'react';
import { Search, X, RotateCcw } from 'lucide-react';
import { CATEGORIES, DECISIONS, EXCEPTION_TYPES, REVIEW_STATUSES } from '../../lib/constants';
import { DECISION_LABEL, EXCEPTION_LABEL, REVIEW_STATUS_LABEL } from '../../lib/labels';

export function FilterBar({ filters, onChange, onReset }) {
  const handleInputChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="filter-bar">
      {/* Search Input */}
      <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
        <Search size={16} style={{ position: 'absolute', left: 10, color: 'var(--color-text-muted)' }} />
        <input
          type="text"
          placeholder="Search ID, Vendor, Invoice #..."
          value={filters.search || ''}
          onChange={(e) => handleInputChange('search', e.target.value)}
          className="filter-input"
          style={{ paddingLeft: 32 }}
        />
        {filters.search && (
          <button
            onClick={() => handleInputChange('search', '')}
            style={{ position: 'absolute', right: 8 }}
            aria-label="Clear search"
          >
            <X size={14} />
          </button>
        )}
      </div>

      {/* Decision Selector */}
      <select
        value={filters.decision || ''}
        onChange={(e) => handleInputChange('decision', e.target.value)}
        className="filter-input"
      >
        <option value="">All Decisions</option>
        {DECISIONS.map((dec) => (
          <option key={dec} value={dec}>
            {DECISION_LABEL[dec] || dec}
          </option>
        ))}
      </select>

      {/* Exception Type Selector */}
      <select
        value={filters.exception_type || ''}
        onChange={(e) => handleInputChange('exception_type', e.target.value)}
        className="filter-input"
      >
        <option value="">All Exception Types</option>
        {EXCEPTION_TYPES.map((type) => (
          <option key={type} value={type}>
            {EXCEPTION_LABEL[type] || type}
          </option>
        ))}
      </select>

      {/* Review Status Selector */}
      <select
        value={filters.review_status || ''}
        onChange={(e) => handleInputChange('review_status', e.target.value)}
        className="filter-input"
      >
        <option value="">All Review Statuses</option>
        {REVIEW_STATUSES.map((status) => (
          <option key={status} value={status}>
            {REVIEW_STATUS_LABEL[status] || status}
          </option>
        ))}
      </select>

      {/* Category Selector */}
      <select
        value={filters.category || ''}
        onChange={(e) => handleInputChange('category', e.target.value)}
        className="filter-input"
      >
        <option value="">All Categories</option>
        {CATEGORIES.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>

      {/* Reset Filters */}
      {onReset && (
        <button
          onClick={onReset}
          className="btn btn-secondary btn-sm"
          title="Reset filters"
          style={{ marginLeft: 'auto' }}
        >
          <RotateCcw size={14} />
          Reset
        </button>
      )}
    </div>
  );
}
