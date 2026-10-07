import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export function ConfidenceHistogram({ histogram = [], autoPassThreshold = 0.85, className = '' }) {
  if (!histogram || histogram.length === 0) return null;

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Confidence Score Distribution</div>
      <div style={{ height: 260, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={histogram} margin={{ left: 10, right: 20, top: 20, bottom: 20 }}>
            <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: '#5B6B7F' }} />
            <YAxis tick={{ fontSize: 11, fill: '#5B6B7F' }} />
            <Tooltip
              formatter={(val) => [`${val} invoices`, 'Count']}
              contentStyle={{ borderRadius: 8, fontSize: 13 }}
            />
            {/* Threshold Line */}
            <ReferenceLine
              x="0.8-0.9"
              stroke="#107C10"
              strokeDasharray="4 4"
              strokeWidth={2}
              label={{
                value: `Threshold (${autoPassThreshold})`,
                position: 'top',
                fill: '#107C10',
                fontSize: 12,
                fontWeight: 600,
              }}
            />
            <Bar dataKey="count" fill="var(--color-primary-hover)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: 8 }}>
        Histogram of confidence scores in 10 buckets from 0.0 to 1.0. Invoices right of the green threshold line are auto-passed.
      </div>
    </div>
  );
}
