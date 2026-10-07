import React, { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatComposer } from './ChatComposer';
import { SuggestedPrompts } from './SuggestedPrompts';
import { Spinner } from '../ui/Spinner';

export function ChatPanel({
  messages = [],
  onSendMessage,
  onFileSelect,
  onProposalConfirm,
  onProposalDismiss,
  onReviewSuccess,
  loading = false,
}) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <ChatMessage
            key={idx}
            message={msg}
            onProposalConfirm={onProposalConfirm}
            onProposalDismiss={onProposalDismiss}
            onReviewSuccess={onReviewSuccess}
          />
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="avatar avatar-ai">B</div>
            <div className="message-bubble" style={{ padding: '8px 16px' }}>
              <Spinner size={16} label="Assistant is thinking & reading verified records..." />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '0 var(--space-4)' }}>
        <SuggestedPrompts onSelectPrompt={onSendMessage} />
      </div>

      <ChatComposer onSend={onSendMessage} onFileSelect={onFileSelect} disabled={loading} />
    </div>
  );
}
