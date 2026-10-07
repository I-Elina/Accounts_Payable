import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { SummaryStrip } from '../components/chat/SummaryStrip';
import { ChatPanel } from '../components/chat/ChatPanel';
import { Toast } from '../components/ui/Toast';

export function Assistant() {
  const [stats, setStats] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState('sess_' + Math.random().toString(36).substring(2, 9));
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  // Fetch initial summary stats
  const fetchStats = async () => {
    try {
      const data = await api.getStats(1);
      setStats(data);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    fetchStats();
    // Initial welcome message
    setMessages([
      {
        role: 'assistant',
        text: 'Hello! I am your Accounts Payable Exception Assistant. Attach an invoice CSV file using the paperclip or ask me a question about exceptions, duplicates, or stats.',
        tools_used: [],
        cards: [],
        proposal: null,
      },
    ]);
  }, []);

  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await api.sendChat(text, sessionId);
      if (res.session_id) setSessionId(res.session_id);

      const aiMsg = {
        role: 'assistant',
        text: res.reply,
        referenced_invoice_ids: res.referenced_invoice_ids || [],
        tools_used: res.tools_used || [],
        cards: res.cards || [],
        proposal: res.proposal || null,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setToast({ message: err.message || 'Failed to send chat message', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (file) => {
    setLoading(true);
    setToast({ message: `Uploading ${file.name}...`, type: 'info' });
    try {
      const uploadRes = await api.uploadFile(file, { useHistory: false });
      setToast({ message: `Successfully processed ${file.name}`, type: 'success' });
      fetchStats();

      // Append upload result message in chat
      const summaryMsg = {
        role: 'assistant',
        text: `Uploaded and processed ${file.name}. Total rows: ${uploadRes.summary.total}. ${uploadRes.summary.auto_pass} auto-passed, ${uploadRes.summary.needs_review} need review, ${uploadRes.summary.exception} exceptions detected.`,
        tools_used: [{ name: 'upload_service', arguments: { filename: file.name } }],
        cards: [
          {
            type: 'stats',
            upload_id: uploadRes.upload_id,
            total: uploadRes.summary.total,
            auto_pass: uploadRes.summary.auto_pass,
            needs_review: uploadRes.summary.needs_review,
            exception: uploadRes.summary.exception,
          },
        ],
        proposal: null,
      };
      setMessages((prev) => [...prev, summaryMsg]);
    } catch (err) {
      setToast({ message: err.message || 'Upload failed', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleProposalConfirm = async (proposal, reviewer) => {
    try {
      await api.reviewInvoice(proposal.id || proposal.invoice_id, {
        action: proposal.action,
        reviewer,
        comment: proposal.reason || 'Approved via AI Proposal confirm',
      });

      setToast({ message: `Done. Logged ${proposal.action} in the audit trail.`, type: 'success' });
      fetchStats();

      // Clear proposal and add response in chat
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.proposal?.invoice_id === proposal.invoice_id) {
            return {
              ...msg,
              proposal: null,
              text: `${msg.text}\n\n✓ Done. Logged ${proposal.action.toUpperCase()} for ${proposal.invoice_id} in the audit trail.`,
            };
          }
          return msg;
        })
      );
    } catch (err) {
      setToast({ message: err.message || 'Failed to review invoice', type: 'error' });
    }
  };

  const handleProposalDismiss = (proposal) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.proposal?.invoice_id === proposal.invoice_id) {
          return { ...msg, proposal: null };
        }
        return msg;
      })
    );
  };

  const handleReviewSuccess = async (id, action, reviewer, comment) => {
    try {
      await api.reviewInvoice(id, { action, reviewer, comment });
      setToast({ message: `Successfully ${action}d invoice`, type: 'success' });
      fetchStats();
    } catch (err) {
      setToast({ message: err.message || 'Review failed', type: 'error' });
    }
  };

  const handleDownloadReport = () => {
    const url = api.reportUrl(1);
    window.open(url, '_blank');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
      <SummaryStrip stats={stats} onDownloadReport={handleDownloadReport} />

      <ChatPanel
        messages={messages}
        onSendMessage={handleSendMessage}
        onFileSelect={handleFileSelect}
        onProposalConfirm={handleProposalConfirm}
        onProposalDismiss={handleProposalDismiss}
        onReviewSuccess={handleReviewSuccess}
        loading={loading}
      />

      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
