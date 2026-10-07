import {
  initialMockUploads,
  initialMockInvoices,
  initialMockAuditLogs,
  initialMockConfig
} from './mockData';

// In-memory state holding arrays
let uploads = [...initialMockUploads];
let invoices = JSON.parse(JSON.stringify(initialMockInvoices));
let auditLogs = [...initialMockAuditLogs];
let configState = JSON.parse(JSON.stringify(initialMockConfig));

const delay = (ms = 150) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockApi = {
  // GET /api/health
  async getHealth() {
    await delay();
    return { status: 'ok', ai_mode: 'mock' };
  },

  // GET /api/uploads
  async getUploads() {
    await delay();
    return { items: [...uploads] };
  },

  // POST /api/uploads
  async uploadFile(file, options = {}) {
    await delay(300);
    const newUploadId = uploads.length + 1;
    const filename = file?.name || 'invoices_uploaded.csv';
    const uploadedBy = options.uploadedBy || 'User';

    const newUpload = {
      id: newUploadId,
      filename,
      uploaded_at: new Date().toISOString(),
      uploaded_by: uploadedBy,
      total_rows: 25,
      auto_pass_count: 18,
      needs_review_count: 5,
      exception_count: 2,
      used_history: options.useHistory ? 1 : 0,
    };

    uploads.unshift(newUpload);

    auditLogs.unshift({
      id: auditLogs.length + 1,
      timestamp: new Date().toISOString(),
      actor: uploadedBy,
      actor_type: 'user',
      event_type: 'UPLOAD_RECEIVED',
      invoice_id: null,
      upload_id: newUploadId,
      details: { filename, size_bytes: file?.size || 45200 },
    });

    auditLogs.unshift({
      id: auditLogs.length + 1,
      timestamp: new Date().toISOString(),
      actor: 'decision-engine',
      actor_type: 'engine',
      event_type: 'INGESTION_COMPLETED',
      invoice_id: null,
      upload_id: newUploadId,
      details: {
        total: 25,
        auto_pass: 18,
        needs_review: 5,
        exception: 2,
      },
    });

    return {
      upload_id: newUploadId,
      filename,
      summary: {
        total: 25,
        auto_pass: 18,
        needs_review: 5,
        exception: 2,
      },
      warnings: [],
    };
  },

  // GET /api/invoices
  async getInvoices(params = {}) {
    await delay();
    let filtered = [...invoices];

    if (params.upload_id) {
      filtered = filtered.filter((inv) => inv.upload_id === Number(params.upload_id));
    }

    if (params.decision) {
      const decList = Array.isArray(params.decision)
        ? params.decision
        : params.decision.split(',').map((d) => d.trim());
      filtered = filtered.filter((inv) => decList.includes(inv.decision.decision));
    }

    if (params.exception_type) {
      filtered = filtered.filter((inv) => inv.decision.exception_type === params.exception_type);
    }

    if (params.review_status) {
      filtered = filtered.filter((inv) => inv.decision.review_status === params.review_status);
    }

    if (params.category) {
      filtered = filtered.filter((inv) => inv.category === params.category);
    }

    if (params.search) {
      const query = params.search.toLowerCase();
      filtered = filtered.filter(
        (inv) =>
          inv.invoice_id.toLowerCase().includes(query) ||
          (inv.invoice_number && inv.invoice_number.toLowerCase().includes(query)) ||
          (inv.vendor_name && inv.vendor_name.toLowerCase().includes(query))
      );
    }

    if (params.min_confidence !== undefined && params.min_confidence !== null) {
      filtered = filtered.filter((inv) => inv.decision.confidence >= Number(params.min_confidence));
    }

    if (params.max_confidence !== undefined && params.max_confidence !== null) {
      filtered = filtered.filter((inv) => inv.decision.confidence <= Number(params.max_confidence));
    }

    // Sorting
    const sortKey = params.sort || 'confidence';
    const order = params.order === 'desc' ? -1 : 1;

    filtered.sort((a, b) => {
      let valA, valB;
      if (sortKey === 'confidence') {
        valA = a.decision.confidence;
        valB = b.decision.confidence;
      } else if (sortKey === 'total_amount') {
        valA = a.total_amount;
        valB = b.total_amount;
      } else if (sortKey === 'invoice_date') {
        valA = a.invoice_date;
        valB = b.invoice_date;
      } else if (sortKey === 'vendor_name') {
        valA = a.vendor_name;
        valB = b.vendor_name;
      } else {
        valA = a.invoice_id;
        valB = b.invoice_id;
      }

      if (valA < valB) return -1 * order;
      if (valA > valB) return 1 * order;
      return 0;
    });

    const page = Number(params.page) || 1;
    const pageSize = Number(params.page_size) || 25;
    const startIndex = (page - 1) * pageSize;
    const paginatedItems = filtered.slice(startIndex, startIndex + pageSize);

    // Map to InvoiceListItem shape
    const items = paginatedItems.map((inv) => ({
      id: inv.id,
      upload_id: inv.upload_id,
      invoice_id: inv.invoice_id,
      invoice_number: inv.invoice_number,
      vendor_name: inv.vendor_name,
      invoice_date: inv.invoice_date,
      total_amount: inv.total_amount,
      currency: inv.currency,
      category: inv.category,
      decision: inv.decision.decision,
      confidence: inv.decision.confidence,
      exception_type: inv.decision.exception_type,
      primary_reason: inv.decision.primary_reason,
      review_status: inv.decision.review_status,
    }));

    return {
      items,
      total: filtered.length,
      page,
      page_size: pageSize,
    };
  },

  // GET /api/invoices/{id}
  async getInvoice(id) {
    await delay();
    const inv = invoices.find((item) => item.id === Number(id) || item.invoice_id === String(id));
    if (!inv) {
      throw {
        code: 'NOT_FOUND',
        message: `Invoice ${id} not found`,
        details: [],
      };
    }

    let matchedInv = null;
    if (inv.decision.matched_record) {
      matchedInv = invoices.find((item) => item.invoice_id === inv.decision.matched_record) || null;
    }

    // Map matched_invoice to basic invoice record shape if present
    const matchedRecord = matchedInv
      ? {
          id: matchedInv.id,
          upload_id: matchedInv.upload_id,
          invoice_id: matchedInv.invoice_id,
          invoice_number: matchedInv.invoice_number,
          vendor_name: matchedInv.vendor_name,
          invoice_date: matchedInv.invoice_date,
          due_date: matchedInv.due_date,
          currency: matchedInv.currency,
          subtotal: matchedInv.subtotal,
          tax_amount: matchedInv.tax_amount,
          total_amount: matchedInv.total_amount,
          category: matchedInv.category,
          po_number: matchedInv.po_number,
          description: matchedInv.description,
        }
      : null;

    return {
      invoice: {
        id: inv.id,
        upload_id: inv.upload_id,
        invoice_id: inv.invoice_id,
        invoice_number: inv.invoice_number,
        vendor_name: inv.vendor_name,
        invoice_date: inv.invoice_date,
        due_date: inv.due_date,
        currency: inv.currency,
        subtotal: inv.subtotal,
        tax_amount: inv.tax_amount,
        total_amount: inv.total_amount,
        category: inv.category,
        po_number: inv.po_number,
        description: inv.description,
      },
      decision: inv.decision,
      matched_invoice: matchedRecord,
      reviews: inv.reviews || [],
    };
  },

  // POST /api/invoices/{id}/summary
  async createSummary(id) {
    await delay(200);
    const inv = invoices.find((item) => item.id === Number(id) || item.invoice_id === String(id));
    if (!inv) {
      throw { code: 'NOT_FOUND', message: `Invoice ${id} not found` };
    }

    if (inv.decision.ai_summary_status !== 'ready') {
      inv.decision.ai_summary_status = 'ready';
      inv.decision.ai_summary = `Invoice ${inv.invoice_id} evaluated with ${inv.decision.confidence} confidence. ${inv.decision.primary_reason}.`;
      inv.decision.ai_suggested_action =
        inv.decision.exception_type === 'fuzzy_duplicate'
          ? 'investigate'
          : inv.decision.decision === 'auto_pass'
          ? 'approve'
          : 'contact_vendor';

      auditLogs.unshift({
        id: auditLogs.length + 1,
        timestamp: new Date().toISOString(),
        actor: 'ai-assistant',
        actor_type: 'ai',
        event_type: 'AI_SUMMARY_GENERATED',
        invoice_id: inv.invoice_id,
        upload_id: inv.upload_id,
        details: {
          suggested_action: inv.decision.ai_suggested_action,
          referenced_rules: inv.decision.violations.map((v) => v.rule_id),
        },
      });
    }

    return {
      ai_summary: inv.decision.ai_summary,
      ai_suggested_action: inv.decision.ai_suggested_action,
      ai_summary_status: inv.decision.ai_summary_status,
    };
  },

  // POST /api/invoices/{id}/review
  async reviewInvoice(id, { action, reviewer, comment }) {
    await delay(200);
    if (!reviewer || !reviewer.trim()) {
      throw { code: 'VALIDATION_ERROR', message: 'Reviewer name is required', details: [] };
    }

    const inv = invoices.find((item) => item.id === Number(id) || item.invoice_id === String(id));
    if (!inv) {
      throw { code: 'NOT_FOUND', message: `Invoice ${id} not found` };
    }

    if (inv.decision.review_status !== 'pending') {
      throw { code: 'CONFLICT', message: `Invoice is already in state '${inv.decision.review_status}' and cannot be reviewed`, details: [] };
    }

    const newStatus = action === 'approve' ? 'approved' : 'rejected';
    inv.decision.review_status = newStatus;

    const reviewEntry = {
      id: (inv.reviews?.length || 0) + 1,
      reviewer,
      action,
      comment: comment || '',
      reviewed_at: new Date().toISOString(),
    };

    inv.reviews = inv.reviews || [];
    inv.reviews.push(reviewEntry);

    const eventType = action === 'approve' ? 'REVIEW_APPROVED' : 'REVIEW_REJECTED';
    auditLogs.unshift({
      id: auditLogs.length + 1,
      timestamp: new Date().toISOString(),
      actor: reviewer,
      actor_type: 'user',
      event_type: eventType,
      invoice_id: inv.invoice_id,
      upload_id: inv.upload_id,
      details: {
        action,
        comment: comment || '',
        previous_confidence: inv.decision.confidence,
      },
    });

    return this.getInvoice(inv.id);
  },

  // GET /api/stats
  async getStats(uploadId) {
    await delay();
    let invList = [...invoices];
    if (uploadId) {
      invList = invList.filter((i) => i.upload_id === Number(uploadId));
    }

    const total = invList.length;
    const auto_pass = invList.filter((i) => i.decision.decision === 'auto_pass').length;
    const needs_review = invList.filter((i) => i.decision.decision === 'needs_review').length;
    const exception = invList.filter((i) => i.decision.decision === 'exception').length;
    const pending_reviews = invList.filter((i) => i.decision.review_status === 'pending').length;

    // Aggregate exception types
    const typeCounts = {};
    invList.forEach((i) => {
      const type = i.decision.exception_type;
      if (type && type !== 'none') {
        typeCounts[type] = (typeCounts[type] || 0) + 1;
      }
    });

    const by_exception_type = Object.entries(typeCounts).map(([exception_type, count]) => ({
      exception_type,
      count,
    }));

    // Generate 10 confidence buckets
    const buckets = [
      '0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
      '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'
    ].map((b) => ({ bucket: b, count: 0 }));

    invList.forEach((i) => {
      const conf = i.decision.confidence;
      let idx = Math.floor(conf * 10);
      if (idx >= 10) idx = 9;
      if (idx < 0) idx = 0;
      buckets[idx].count++;
    });

    return {
      upload_id: uploadId ? Number(uploadId) : 1,
      total,
      by_decision: { auto_pass, needs_review, exception },
      auto_pass_rate: total > 0 ? auto_pass / total : 0,
      pending_reviews,
      by_exception_type,
      confidence_histogram: buckets,
      estimated_minutes_saved: auto_pass * 5,
    };
  },

  // GET /api/audit
  async getAudit(params = {}) {
    await delay();
    let filtered = [...auditLogs];

    if (params.upload_id) {
      filtered = filtered.filter((log) => log.upload_id === Number(params.upload_id));
    }
    if (params.invoice_id) {
      filtered = filtered.filter((log) => log.invoice_id === params.invoice_id);
    }
    if (params.event_type) {
      filtered = filtered.filter((log) => log.event_type === params.event_type);
    }

    const page = Number(params.page) || 1;
    const pageSize = Number(params.page_size) || 25;
    const startIndex = (page - 1) * pageSize;
    const items = filtered.slice(startIndex, startIndex + pageSize);

    return {
      items,
      total: filtered.length,
      page,
      page_size: pageSize,
    };
  },

  // GET /api/config
  async getConfig() {
    await delay();
    return { ...configState };
  },

  // PUT /api/config
  async putConfig(body) {
    await delay(200);
    if (body.auto_pass_threshold !== undefined) {
      configState.auto_pass_threshold = Number(body.auto_pass_threshold);
    }
    if (body.exception_below !== undefined) {
      configState.exception_below = Number(body.exception_below);
    }

    auditLogs.unshift({
      id: auditLogs.length + 1,
      timestamp: new Date().toISOString(),
      actor: 'system',
      actor_type: 'system',
      event_type: 'SETTINGS_CHANGED',
      invoice_id: null,
      upload_id: null,
      details: {
        auto_pass_threshold: configState.auto_pass_threshold,
        exception_below: configState.exception_below,
      },
    });

    return { ...configState };
  },

  // GET /api/uploads/{id}/report
  reportUrl(uploadId = 1, decision = 'needs_review,exception') {
    return `/mock_report.csv`;
  },

  // POST /api/chat
  async sendChat(message, sessionId = 'sess_default', uploadId = null) {
    await delay(300);
    const msg = message.trim().toLowerCase();

    auditLogs.unshift({
      id: auditLogs.length + 1,
      timestamp: new Date().toISOString(),
      actor: 'ai-assistant',
      actor_type: 'ai',
      event_type: 'CHAT_QUERY',
      invoice_id: null,
      upload_id: uploadId || 1,
      details: { query: message, session_id: sessionId },
    });

    // Match intents
    if (msg.includes('why') && (msg.includes('inv-') || msg.includes('1042'))) {
      const inv = invoices.find((i) => i.invoice_id === 'INV-1042') || invoices[0];
      return {
        reply: `Invoice ${inv.invoice_id} (${inv.vendor_name}) was flagged as a ${inv.decision.exception_type.replace('_', ' ')}. ${inv.decision.primary_reason}. Both records share invoice number ${inv.invoice_number} and near-identical amounts issued 1 day apart.`,
        session_id: sessionId,
        referenced_invoice_ids: [inv.invoice_id, inv.decision.matched_record].filter(Boolean),
        tools_used: [{ name: 'explain_decision', arguments: { invoice_id: inv.invoice_id } }],
        cards: [
          {
            type: 'invoice',
            id: inv.id,
            invoice_id: inv.invoice_id,
            vendor_name: inv.vendor_name,
            total_amount: inv.total_amount,
            currency: inv.currency,
            decision: inv.decision.decision,
            confidence: inv.decision.confidence,
            primary_reason: inv.decision.primary_reason,
            matched_record: inv.decision.matched_record,
            review_status: inv.decision.review_status,
          },
        ],
        proposal: {
          type: 'review_proposal',
          id: inv.id,
          invoice_id: inv.invoice_id,
          action: 'reject',
          reason: `Probable duplicate of ${inv.decision.matched_record} with vendor invoice number ${inv.invoice_number}`,
        },
      };
    }

    if (msg.includes('riskiest') || msg.includes('pending') || msg.includes('queue') || msg.includes('show')) {
      const pendingInvoices = invoices
        .filter((i) => i.decision.review_status === 'pending')
        .sort((a, b) => a.decision.confidence - b.decision.confidence)
        .slice(0, 5);

      const cards = pendingInvoices.map((inv) => ({
        type: 'invoice',
        id: inv.id,
        invoice_id: inv.invoice_id,
        vendor_name: inv.vendor_name,
        total_amount: inv.total_amount,
        currency: inv.currency,
        decision: inv.decision.decision,
        confidence: inv.decision.confidence,
        primary_reason: inv.decision.primary_reason,
        matched_record: inv.decision.matched_record,
        review_status: inv.decision.review_status,
      }));

      return {
        reply: `Here are the top ${pendingInvoices.length} riskiest pending invoices requiring human review, ordered by confidence score (lowest confidence first):`,
        session_id: sessionId,
        referenced_invoice_ids: pendingInvoices.map((i) => i.invoice_id),
        tools_used: [{ name: 'list_pending', arguments: { limit: 5 } }],
        cards,
        proposal: null,
      };
    }

    if (msg.includes('duplicate')) {
      const dupInvoices = invoices.filter(
        (i) => i.decision.exception_type === 'fuzzy_duplicate' || i.decision.exception_type === 'exact_duplicate'
      );

      const cards = dupInvoices.slice(0, 5).map((inv) => ({
        type: 'invoice',
        id: inv.id,
        invoice_id: inv.invoice_id,
        vendor_name: inv.vendor_name,
        total_amount: inv.total_amount,
        currency: inv.currency,
        decision: inv.decision.decision,
        confidence: inv.decision.confidence,
        primary_reason: inv.decision.primary_reason,
        matched_record: inv.decision.matched_record,
        review_status: inv.decision.review_status,
      }));

      return {
        reply: `Found ${dupInvoices.length} duplicate invoice flags in the dataset. Here are the main candidates:`,
        session_id: sessionId,
        referenced_invoice_ids: dupInvoices.map((i) => i.invoice_id),
        tools_used: [{ name: 'list_duplicates', arguments: { limit: 10 } }],
        cards,
        proposal: null,
      };
    }

    if (msg.includes('report') || msg.includes('download') || msg.includes('csv')) {
      return {
        reply: `You can download the exception report CSV containing all flagged invoices for offline audit or Excel review. Click the button below:`,
        session_id: sessionId,
        referenced_invoice_ids: [],
        tools_used: [{ name: 'get_report_link', arguments: { upload_id: 1 } }],
        cards: [
          {
            type: 'report',
            upload_id: 1,
            url: '/mock_report.csv',
          },
        ],
        proposal: null,
      };
    }

    if (msg.includes('approve') || msg.includes('reject')) {
      const match = message.match(/(INV-\d+|[A-Z]{2,5}-\d+)/i);
      const targetId = match ? match[1].toUpperCase() : 'INV-1042';
      const action = msg.includes('approve') ? 'approve' : 'reject';
      const inv = invoices.find((i) => i.invoice_id === targetId) || invoices[0];

      return {
        reply: `I suggest ${action}ing invoice ${inv.invoice_id} based on the rule evaluation evidence. Please click the confirm button to execute the review action:`,
        session_id: sessionId,
        referenced_invoice_ids: [inv.invoice_id],
        tools_used: [{ name: 'propose_review', arguments: { invoice_id: inv.invoice_id, action } }],
        cards: [
          {
            type: 'invoice',
            id: inv.id,
            invoice_id: inv.invoice_id,
            vendor_name: inv.vendor_name,
            total_amount: inv.total_amount,
            currency: inv.currency,
            decision: inv.decision.decision,
            confidence: inv.decision.confidence,
            primary_reason: inv.decision.primary_reason,
            matched_record: inv.decision.matched_record,
            review_status: inv.decision.review_status,
          },
        ],
        proposal: {
          type: 'review_proposal',
          id: inv.id,
          invoice_id: inv.invoice_id,
          action,
          reason: `Assistant proposal to ${action} ${inv.invoice_id}`,
        },
      };
    }

    // Default stats answer
    const statsObj = await this.getStats(1);
    return {
      reply: `I am your Accounts Payable Exception Assistant. Upload an invoice batch or ask me questions. Currently, out of ${statsObj.total} invoices, ${statsObj.by_decision.auto_pass} auto-passed (${(statsObj.auto_pass_rate * 100).toFixed(1)}%), ${statsObj.by_decision.needs_review} need review, and ${statsObj.by_decision.exception} exceptions were caught.`,
      session_id: sessionId,
      referenced_invoice_ids: [],
      tools_used: [{ name: 'get_stats', arguments: {} }],
      cards: [
        {
          type: 'stats',
          upload_id: 1,
          total: statsObj.total,
          auto_pass: statsObj.by_decision.auto_pass,
          needs_review: statsObj.by_decision.needs_review,
          exception: statsObj.by_decision.exception,
        },
      ],
      proposal: null,
    };
  },
};
