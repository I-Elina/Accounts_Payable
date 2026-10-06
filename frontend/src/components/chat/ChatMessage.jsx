import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, User, Wrench } from 'lucide-react';
import { CardRenderer } from './CardRenderer';
import { ProposalConfirm } from './ProposalConfirm';

export function ChatMessage({ message, onProposalConfirm, onProposalDismiss, onReviewSuccess }) {
  const navigate = useNavigate();
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-ai'}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      <div className="message-bubble">
        {/* Reply Text */}
        <div>{message.text}</div>

        {/* Tools Used Badge */}
        {!isUser && message.tools_used && message.tools_used.length > 0 && (
          <div
            style={{
              fontSize: '11px',
              color: 'var(--color-text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Wrench size={10} />
            <span>Tools used: {message.tools_used.map((t) => t.name).join(', ')}</span>
          </div>
        )}

        {/* Referenced Invoice IDs */}
        {!isUser && message.referenced_invoice_ids && message.referenced_invoice_ids.length > 0 && (
          <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-text-muted)' }}>
            Referenced Invoices:{' '}
            {message.referenced_invoice_ids.map((id, idx) => (
              <React.Fragment key={id}>
                <button
                  onClick={() => navigate(`/invoices?search=${id}`)}
                  className="font-mono"
                  style={{
                    color: 'var(--color-primary)',
                    fontWeight: 600,
                    textDecoration: 'underline',
                  }}
                >
                  {id}
                </button>
                {idx < message.referenced_invoice_ids.length - 1 ? ', ' : ''}
              </React.Fragment>
            ))}
          </div>
        )}

        {/* Render Cards */}
        {!isUser && message.cards && message.cards.length > 0 && (
          <div className="chat-cards-container">
            {message.cards.map((card, idx) => (
              <CardRenderer key={idx} card={card} onReviewSuccess={onReviewSuccess} />
            ))}
          </div>
        )}

        {/* Render Proposal Bar */}
        {!isUser && message.proposal && (
          <ProposalConfirm
            proposal={message.proposal}
            onConfirm={onProposalConfirm}
            onDismiss={onProposalDismiss}
          />
        )}
      </div>
    </div>
  );
}
