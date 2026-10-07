import React, { useState, useEffect } from 'react';
import { Sliders, Save, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';
import { useApi } from '../hooks/useApi';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { Toast } from '../components/ui/Toast';
import { DataTable } from '../components/ui/DataTable';

export function Settings() {
  const { data: config, loading, error, refetch } = useApi(api.getConfig);
  const [autoPassThreshold, setAutoPassThreshold] = useState(0.85);
  const [exceptionBelow, setExceptionBelow] = useState(0.40);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (config) {
      if (config.auto_pass_threshold !== undefined) setAutoPassThreshold(config.auto_pass_threshold);
      if (config.exception_below !== undefined) setExceptionBelow(config.exception_below);
    }
  }, [config]);

  const handleSave = async (e) => {
    e.preventDefault();
    const passVal = Number(autoPassThreshold);
    const excVal = Number(exceptionBelow);

    if (isNaN(passVal) || isNaN(excVal)) {
      setToast({ message: 'Threshold values must be numbers between 0.0 and 1.0', type: 'error' });
      return;
    }

    if (passVal < 0 || passVal > 1 || excVal < 0 || excVal > 1) {
      setToast({ message: 'Thresholds must be between 0.0 and 1.0', type: 'error' });
      return;
    }

    if (excVal >= passVal) {
      setToast({ message: 'Exception threshold must be strictly less than auto-pass threshold', type: 'error' });
      return;
    }

    setSaving(true);
    try {
      await api.putConfig({
        auto_pass_threshold: passVal,
        exception_below: excVal,
      });
      setToast({ message: 'Engine settings updated successfully. Applies to future uploads.', type: 'success' });
      refetch();
    } catch (err) {
      setToast({ message: err.message || 'Failed to update settings', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const ruleColumns = [
    {
      header: 'Rule ID',
      key: 'rule_id',
      render: (val) => <span className="font-mono" style={{ fontWeight: 700 }}>{val}</span>,
    },
    {
      header: 'Rule Name',
      key: 'name',
      render: (val) => <strong>{val}</strong>,
    },
    {
      header: 'Severity',
      key: 'severity',
      render: (val) => (
        <span
          style={{
            fontSize: 'var(--fs-xs)',
            padding: '2px 8px',
            borderRadius: 4,
            fontWeight: 600,
            backgroundColor: val === 'hard' ? 'var(--color-exception-bg)' : 'var(--color-review-bg)',
            color: val === 'hard' ? 'var(--color-exception)' : 'var(--color-review)',
          }}
        >
          {val.toUpperCase()}
        </span>
      ),
    },
    {
      header: 'Penalty',
      key: 'penalty',
      render: (val) => <span className="penalty-tag">−{Number(val).toFixed(2)}</span>,
    },
    {
      header: 'Exception Category',
      key: 'exception_type',
      render: (val) => <span style={{ fontFamily: 'var(--font-mono)' }}>{val}</span>,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', maxWidth: 1000, margin: '0 auto', width: '100%' }}>
      <div>
        <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Rule Engine Configuration</h2>
        <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
          Tune decision confidence thresholds and inspect active rule penalties.
        </span>
      </div>

      {loading && <Spinner label="Loading threshold settings..." />}
      {error && <ErrorState error={error} onRetry={refetch} />}

      {!loading && !error && config && (
        <>
          {/* Threshold Tuning Form */}
          <form onSubmit={handleSave} className="card">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Sliders size={18} style={{ color: 'var(--color-primary)' }} />
              <span>Decision Confidence Thresholds</span>
            </div>

            <div
              style={{
                fontSize: 'var(--fs-xs)',
                color: 'var(--color-text-muted)',
                backgroundColor: 'var(--color-primary-soft)',
                padding: 'var(--space-3)',
                borderRadius: 'var(--radius)',
                marginBottom: 'var(--space-4)',
                borderLeft: '4px solid var(--color-primary)',
              }}
            >
              ℹ️ <strong>Note:</strong> Changes to confidence thresholds write a <code>SETTINGS_CHANGED</code> audit event and apply to all <strong>future batch uploads</strong>. Existing decision scores are preserved.
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
              <div>
                <label style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>
                  Auto-Pass Threshold (Default 0.85)
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.0"
                  max="1.0"
                  className="filter-input"
                  style={{ width: '100%' }}
                  value={autoPassThreshold}
                  onChange={(e) => setAutoPassThreshold(e.target.value)}
                />
                <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', display: 'block', marginTop: 4 }}>
                  Invoices scoring ≥ {autoPassThreshold} with no hard violations auto-pass cleanly.
                </span>
              </div>

              <div>
                <label style={{ fontSize: 'var(--fs-xs)', fontWeight: 600, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>
                  Exception Below Threshold (Default 0.40)
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.0"
                  max="1.0"
                  className="filter-input"
                  style={{ width: '100%' }}
                  value={exceptionBelow}
                  onChange={(e) => setExceptionBelow(e.target.value)}
                />
                <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', display: 'block', marginTop: 4 }}>
                  Invoices scoring &lt; {exceptionBelow} are routed directly to Exception status.
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--space-4)' }}>
              <Button type="submit" variant="primary" icon={Save} disabled={saving}>
                {saving ? 'Saving Settings...' : 'Save Configuration'}
              </Button>
            </div>
          </form>

          {/* Read-only Rule Catalogue Table */}
          <div>
            <h3 style={{ fontSize: 'var(--fs-md)', fontWeight: 700, marginBottom: 'var(--space-3)' }}>
              Active Decision Rules Catalogue (R01–R11)
            </h3>
            <DataTable columns={ruleColumns} data={config.rules || []} />
          </div>
        </>
      )}

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
