import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { EXCEPTION_LABEL } from '../../lib/labels';

export function ExceptionsByTypeBar({ byExceptionType = [], className = '' }) {
  if (!byExceptionType || byExceptionType.length === 0) return null;

  const data = byExceptionType.map((item) => ({
    type: item.exception_type,
    label: EXCEPTION_LABEL[item.exception_type] || item.exception_type,
    count: item.count,
  }));

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Exceptions & Flags by Type</div>
      <div style={{ height: 260, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
            <XAxis type="number" />
            <YAxis
              type="category"
              dataKey="label"
              width={140}
              tick={{ fontSize: 12, fill: '#5B6B7F' }}
            />
            <Tooltip
              formatter={(val) => [`${val} invoices`, 'Count']}
              contentStyle={{ borderRadius: 8, fontSize: 13 }}
            />
            <Bar dataKey="count" fill="var(--color-primary)" radius={[0, 4, 4, 0]}>
              {data.map((entry, idx) => (
                <Cell
                  key={idx}
                  fill={
                    entry.type === 'exact_duplicate' || entry.type === 'fuzzy_duplicate'
                      ? '#B35C00'
                      : 'var(--color-primary)'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: 8 }}>
        Breakdown of rule violation flags by exception type.
      </div>
    </div>
  );
}
