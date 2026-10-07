import React, { useState } from 'react';
import { BarChart3, CheckCircle2, AlertTriangle, XCircle, Clock, Zap } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { StatTile } from '../components/ui/StatTile';
import { DecisionDonut } from '../components/charts/DecisionDonut';
import { ExceptionsByTypeBar } from '../components/charts/ExceptionsByTypeBar';
import { ConfidenceHistogram } from '../components/charts/ConfidenceHistogram';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';

export function Dashboard() {
  const [selectedUploadId, setSelectedUploadId] = useState('');

  const { data: uploadsData } = useApi(api.getUploads);
  const { data: configData } = useApi(api.getConfig);

  const fetchStats = () => api.getStats(selectedUploadId || undefined);
  const { data: stats, loading: statsLoading, error: statsError, refetch } = useApi(fetchStats, [selectedUploadId]);

  const uploads = uploadsData?.items || [];
  const autoPassThreshold = configData?.auto_pass_threshold || 0.85;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {/* Header with Upload Batch Selector */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Analytics & Accuracy Dashboard</h2>
          <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
            Real-time rule engine distribution metrics and threshold calibration performance.
          </span>
        </div>

        {/* Upload Selector Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <label style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--color-text-muted)' }}>
            Select Batch:
          </label>
          <select
            className="filter-input"
            value={selectedUploadId}
            onChange={(e) => setSelectedUploadId(e.target.value)}
          >
            <option value="">All Upload Batches</option>
            {uploads.map((u) => (
              <option key={u.id} value={u.id}>
                #{u.id} — {u.filename} ({u.total_rows} rows)
              </option>
            ))}
          </select>
        </div>
      </div>

      {statsLoading && <Spinner label="Loading dashboard metrics..." />}
      {statsError && <ErrorState error={statsError} onRetry={refetch} />}

      {!statsLoading && !statsError && stats && (
        <>
          {/* Stat Tiles Row */}
          <div className="stat-grid">
            <StatTile
              label="Total Invoices"
              value={stats.total}
              subtext="Batch size processed"
              icon={BarChart3}
            />

            <StatTile
              label="Auto-Pass Rate"
              value={`${(stats.auto_pass_rate * 100).toFixed(1)}%`}
              subtext={`${stats.by_decision.auto_pass} passed automatically`}
              icon={CheckCircle2}
            />

            <StatTile
              label="Needs Review"
              value={stats.by_decision.needs_review}
              subtext="Flagged for soft violation"
              icon={AlertTriangle}
            />

            <StatTile
              label="Exceptions"
              value={stats.by_decision.exception}
              subtext="Hard violations caught"
              icon={XCircle}
            />

            <StatTile
              label="Pending Reviews"
              value={stats.pending_reviews}
              subtext="Awaiting reviewer action"
              icon={Clock}
            />

            <StatTile
              label="Time Saved (estimate)"
              value={`${Math.round(stats.estimated_minutes_saved / 60)} hrs`}
              subtext={`~5 mins saved per auto-pass`}
              icon={Zap}
            />
          </div>

          {/* Charts Row 1: Decision Donut & Exceptions Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
            <DecisionDonut byDecision={stats.by_decision} total={stats.total} />
            <ExceptionsByTypeBar byExceptionType={stats.by_exception_type} />
          </div>

          {/* Charts Row 2: Confidence Histogram */}
          <ConfidenceHistogram
            histogram={stats.confidence_histogram}
            autoPassThreshold={autoPassThreshold}
          />
        </>
      )}
    </div>
  );
}
