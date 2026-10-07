import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { AttachButton } from './AttachButton';

export function ChatComposer({ onSend, onFileSelect, disabled = false }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <form onSubmit={handleSubmit} className="chat-composer">
      <AttachButton onFileSelect={onFileSelect} disabled={disabled} />
      <input
        type="text"
        className="chat-input"
        placeholder="Ask the assistant anything (e.g., 'Why was INV-1042 flagged?' or 'Show riskiest')..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
      />
      <button
        type="submit"
        className="btn btn-primary"
        disabled={!text.trim() || disabled}
        style={{ borderRadius: 20, padding: '8px 16px' }}
      >
        <Send size={16} />
      </button>
    </form>
  );
}
