import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { DECISION_LABEL } from '../../lib/labels';

const COLOR_MAP = {
  auto_pass: '#107C10',
  needs_review: '#B35C00',
  exception: '#C42B31',
};

export function DecisionDonut({ byDecision, total = 0, className = '' }) {
  if (!byDecision) return null;

  const data = [
    { key: 'auto_pass', name: DECISION_LABEL.auto_pass, value: byDecision.auto_pass || 0 },
    { key: 'needs_review', name: DECISION_LABEL.needs_review, value: byDecision.needs_review || 0 },
    { key: 'exception', name: DECISION_LABEL.exception, value: byDecision.exception || 0 },
  ].filter((item) => item.value >= 0);

  return (
    <div className={`card ${className}`}>
      <div className="card-title">Invoices by Decision</div>
      <div style={{ height: 260, width: '100%', position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry) => (
                <Cell key={entry.key} fill={COLOR_MAP[entry.key]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(val, name) => [`${val} invoices`, name]}
              contentStyle={{ borderRadius: 8, fontSize: 13 }}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: 8 }}>
        Summary chart showing distribution of {total} total uploaded invoices across Auto-pass, Needs review, and Exception categories.
      </div>
    </div>
  );
}
