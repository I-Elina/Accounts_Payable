import React from 'react';
import { Sparkles } from 'lucide-react';

const PROMPTS = [
  'Show the riskiest invoices',
  'Why was INV-1042 flagged?',
  'Show all duplicates',
  'Download the report',
  'What happened to INV-1042?',
];

export function SuggestedPrompts({ onSelectPrompt }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap', margin: 'var(--space-2) 0' }}>
      <span style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
        <Sparkles size={12} color="var(--color-primary)" />
        Suggested:
      </span>
      {PROMPTS.map((prompt) => (
        <button
          key={prompt}
          onClick={() => onSelectPrompt(prompt)}
          style={{
            fontSize: 'var(--fs-xs)',
            backgroundColor: 'var(--color-primary-soft)',
            color: 'var(--color-primary)',
            padding: '4px 10px',
            borderRadius: 14,
            fontWeight: 500,
            border: '1px solid transparent',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => (e.target.style.borderColor = 'var(--color-primary)')}
          onMouseLeave={(e) => (e.target.style.borderColor = 'transparent')}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}
