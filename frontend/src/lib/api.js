import { mockApi } from '../mocks/mockApi';

const isMock = import.meta.env.VITE_USE_MOCK === 'true' || import.meta.env.VITE_USE_MOCK === true;

async function request(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData = { code: 'INTERNAL', message: response.statusText, details: [] };
    try {
      const parsed = await response.json();
      if (parsed && parsed.error) {
        errorData = parsed.error;
      }
    } catch (e) {
      // JSON parse error
    }
    throw errorData;
  }

  return response.json();
}

export const api = {
  async getHealth() {
    if (isMock) return mockApi.getHealth();
    return request('/api/health');
  },

  async getUploads() {
    if (isMock) return mockApi.getUploads();
    return request('/api/uploads');
  },

  async uploadFile(file, options = {}) {
    if (isMock) return mockApi.uploadFile(file, options);

    const formData = new FormData();
    formData.append('file', file);
    if (options.uploadedBy) formData.append('uploaded_by', options.uploadedBy);
    if (options.useHistory) formData.append('use_history', 'true');

    const response = await fetch('/api/uploads', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let errorData = { code: 'VALIDATION_ERROR', message: 'Upload failed', details: [] };
      try {
        const parsed = await response.json();
        if (parsed && parsed.error) errorData = parsed.error;
      } catch (e) {}
      throw errorData;
    }

    return response.json();
  },

  async getInvoices(params = {}) {
    if (isMock) return mockApi.getInvoices(params);
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    return request(`/api/invoices?${query.toString()}`);
  },

  async getInvoice(id) {
    if (isMock) return mockApi.getInvoice(id);
    return request(`/api/invoices/${id}`);
  },

  async createSummary(id) {
    if (isMock) return mockApi.createSummary(id);
    return request(`/api/invoices/${id}/summary`, { method: 'POST' });
  },

  async reviewInvoice(id, { action, reviewer, comment }) {
    if (isMock) return mockApi.reviewInvoice(id, { action, reviewer, comment });
    return request(`/api/invoices/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, reviewer, comment }),
    });
  },

  async getStats(uploadId) {
    if (isMock) return mockApi.getStats(uploadId);
    const url = uploadId ? `/api/stats?upload_id=${uploadId}` : '/api/stats';
    return request(url);
  },

  async getAudit(params = {}) {
    if (isMock) return mockApi.getAudit(params);
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    return request(`/api/audit?${query.toString()}`);
  },

  async sendChat(message, sessionId = null, uploadId = null) {
    if (isMock) return mockApi.sendChat(message, sessionId, uploadId);
    return request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId, upload_id: uploadId }),
    });
  },

  async getConfig() {
    if (isMock) return mockApi.getConfig();
    return request('/api/config');
  },

  async putConfig(body) {
    if (isMock) return mockApi.putConfig(body);
    return request('/api/config', {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  reportUrl(uploadId = 1, decision = 'needs_review,exception') {
    if (isMock) return mockApi.reportUrl(uploadId, decision);
    return `/api/uploads/${uploadId}/report?decision=${encodeURIComponent(decision)}`;
  },
};
