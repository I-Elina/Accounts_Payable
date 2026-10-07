import React, { useRef } from 'react';
import { Paperclip } from 'lucide-react';

export function AttachButton({ onFileSelect, disabled = false }) {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onFileSelect) {
      onFileSelect(file);
    }
    // reset input value so re-selecting same file triggers change
    e.target.value = '';
  };

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".csv, .xlsx"
        style={{ display: 'none' }}
      />
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className="btn btn-secondary btn-sm"
        title="Attach invoice CSV/Excel file"
        style={{ padding: '6px 10px' }}
      >
        <Paperclip size={16} />
      </button>
    </>
  );
}
