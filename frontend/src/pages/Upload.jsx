import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { Toast } from '../components/ui/Toast';
import { useReviewer } from '../hooks/useReviewer';

export function Upload() {
  const navigate = useNavigate();
  const [reviewer] = useReviewer();
  const [useHistory, setUseHistory] = useState(false);
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorPayload, setErrorPayload] = useState(null);
  const [toast, setToast] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (f) => {
    setErrorPayload(null);
    setResult(null);
    const ext = f.name.split('.').pop().toLowerCase();
    if (ext !== 'csv' && ext !== 'xlsx') {
      setToast({ message: 'Only .csv and .xlsx files are supported', type: 'error' });
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setToast({ message: 'File size exceeds 10 MB limit', type: 'error' });
      return;
    }
    setFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setErrorPayload(null);
    setResult(null);

    try {
      const res = await api.uploadFile(file, {
        uploadedBy: reviewer || 'User',
        useHistory,
      });
      setResult(res);
      setToast({ message: `Batch ${file.name} uploaded successfully`, type: 'success' });
    } catch (err) {
      setErrorPayload(err);
      setToast({ message: err.message || 'Upload failed', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', maxWidth: 800, margin: '0 auto', width: '100%' }}>
      <div>
        <h2 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700 }}>Upload Invoice Batch</h2>
        <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
          Upload AP invoice CSV or Excel files (up to 10 MB). The decision engine will automatically evaluate rules.
        </span>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${isDragging ? 'var(--color-primary)' : 'var(--color-border)'}`,
          backgroundColor: isDragging ? 'var(--color-primary-soft)' : 'var(--color-surface)',
          borderRadius: 'var(--radius)',
          padding: 'var(--space-6)',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--space-3)',
          transition: 'all 0.15s ease',
          cursor: 'pointer',
        }}
        onClick={() => document.getElementById('batch-file-input').click()}
      >
        <input
          id="batch-file-input"
          type="file"
          accept=".csv, .xlsx"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <UploadCloud size={48} color="var(--color-primary)" />
        <div style={{ fontWeight: 600, fontSize: 'var(--fs-md)' }}>
          {file ? file.name : 'Drag & drop invoice CSV/Excel here, or click to browse'}
        </div>
        <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
          Supported formats: .csv, .xlsx (Max 10 MB)
        </div>
        {file && (
          <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-primary)', fontWeight: 600 }}>
            File selected: {(file.size / 1024).toFixed(1)} KB
          </div>
        )}
      </div>

      {/* Checkbox Options */}
      <div className="card" style={{ padding: 'var(--space-3) var(--space-4)' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={useHistory}
            onChange={(e) => setUseHistory(e.target.checked)}
            style={{ width: 16, height: 16 }}
          />
          <div>
            <span style={{ fontWeight: 600 }}>Also compare with earlier uploads (use_history)</span>
            <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
              Check this option when uploading incremental files to detect duplicates across previous uploads. Default is off to prevent self-duplication on re-upload.
            </div>
          </div>
        </label>
      </div>

      {/* Upload Action Button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="primary" size="lg" disabled={!file || loading} onClick={handleSubmit}>
          {loading ? 'Processing Batch...' : 'Process Invoice Batch'}
        </Button>
      </div>

      {loading && <Spinner label="Running rule engine evaluation on batch..." />}

      {/* Error Details (422) */}
      {errorPayload && (
        <div className="card" style={{ borderColor: 'var(--color-exception)', backgroundColor: 'var(--color-exception-bg)' }}>
          <div className="card-title" style={{ color: 'var(--color-exception)' }}>
            Validation / Ingestion Error ({errorPayload.code})
          </div>
          <p style={{ fontSize: 'var(--fs-sm)', marginBottom: 'var(--space-2)' }}>{errorPayload.message}</p>
          {errorPayload.details && errorPayload.details.length > 0 && (
            <ul style={{ paddingLeft: 'var(--space-4)', fontSize: 'var(--fs-xs)', color: 'var(--color-exception)' }}>
              {errorPayload.details.map((detail, idx) => (
                <li key={idx}>{detail}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Ingestion Results Summary Card */}
      {result && (
        <div className="card" style={{ borderColor: 'var(--color-pass)', backgroundColor: 'var(--color-pass-bg)' }}>
          <div className="card-title" style={{ color: 'var(--color-pass)' }}>
            ✓ Batch Ingestion Completed (Upload #{result.upload_id})
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-4)', margin: 'var(--space-3) 0' }}>
            <div style={{ backgroundColor: 'var(--color-surface)', padding: 'var(--space-3)', borderRadius: 'var(--radius)', textCenter: 'center' }}>
              <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-pass)', fontWeight: 600 }}>Auto-passed</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-pass)' }}>
                {result.summary.auto_pass}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-surface)', padding: 'var(--space-3)', borderRadius: 'var(--radius)', textCenter: 'center' }}>
              <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-review)', fontWeight: 600 }}>Needs Review</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-review)' }}>
                {result.summary.needs_review}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-surface)', padding: 'var(--space-3)', borderRadius: 'var(--radius)', textCenter: 'center' }}>
              <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-exception)', fontWeight: 600 }}>Exceptions</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-exception)' }}>
                {result.summary.exception}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--space-3)' }}>
            <Button
              variant="primary"
              onClick={() => navigate('/queue')}
              icon={ArrowRight}
            >
              Go to Review Queue
            </Button>
          </div>
        </div>
      )}

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
