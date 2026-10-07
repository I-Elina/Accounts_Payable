export const initialMockUploads = [
  {
    id: 1,
    filename: "invoices_demo.csv",
    uploaded_at: "2026-10-07T10:04:55Z",
    uploaded_by: "Shree",
    total_rows: 1000,
    auto_pass_count: 816,
    needs_review_count: 90,
    exception_count: 94,
    used_history: 0
  }
];

export const initialMockInvoices = [
  {
    id: 7,
    upload_id: 1,
    invoice_id: "INV-1042",
    invoice_number: "AC/2026/0345",
    vendor_name: "Acme Pvt Ltd",
    invoice_date: "2026-09-03",
    due_date: "2026-10-03",
    currency: "INR",
    subtotal: 8474.58,
    tax_amount: 1525.42,
    total_amount: 10000.0,
    category: "Office Supplies",
    po_number: "PO-8821",
    description: "Stationery and printer cartridges",
    decision: {
      decision: "needs_review",
      confidence: 0.50,
      pass_resolved_in: 2,
      exception_type: "fuzzy_duplicate",
      primary_reason: "Probable duplicate of INV-0987 (96% similar)",
      matched_record: "INV-0987",
      violations: [
        {
          rule_id: "R09",
          name: "Fuzzy duplicate",
          severity: "soft",
          penalty: 0.35,
          exception_type: "fuzzy_duplicate",
          message: "Probable duplicate of INV-0987 (96% similar)",
          matched_record: "INV-0987",
          evidence: {
            vendor_similarity: 0.94,
            invoice_number_similarity: 1.0,
            amount_difference_pct: 0.2,
            days_apart: 1,
            combined_similarity: 0.96
          }
        },
        {
          rule_id: "R10",
          name: "Near-identical amount",
          severity: "soft",
          penalty: 0.15,
          exception_type: "fuzzy_duplicate",
          message: "Amount within 0.2% of matched record INV-0987",
          matched_record: "INV-0987",
          evidence: { amount_difference_pct: 0.2 }
        }
      ],
      evidence: { matched_invoice_id: "INV-0987" },
      ai_summary: "Invoice INV-1042 was flagged as a probable duplicate of INV-0987. Both share vendor invoice number AC/2026/0345 and near-identical totals (₹10,000.00 vs ₹10,020.00) issued 1 day apart.",
      ai_suggested_action: "investigate",
      ai_summary_status: "ready",
      review_status: "pending"
    },
    reviews: []
  },
  {
    id: 1,
    upload_id: 1,
    invoice_id: "INV-0987",
    invoice_number: "AC/2026/0345",
    vendor_name: "Acme Private Limited",
    invoice_date: "2026-09-02",
    due_date: "2026-10-02",
    currency: "INR",
    subtotal: 8491.53,
    tax_amount: 1528.47,
    total_amount: 10020.0,
    category: "Office Supplies",
    po_number: "PO-8821",
    description: "Office paper and supplies",
    decision: {
      decision: "auto_pass",
      confidence: 1.00,
      pass_resolved_in: 1,
      exception_type: "none",
      primary_reason: "No issues found",
      matched_record: null,
      violations: [],
      evidence: {},
      ai_summary: null,
      ai_suggested_action: "approve",
      ai_summary_status: "not_generated",
      review_status: "not_required"
    },
    reviews: []
  },
  {
    id: 6,
    upload_id: 1,
    invoice_id: "INV-1041",
    invoice_number: "AC/2026/0344",
    vendor_name: "Acme Private Limited",
    invoice_date: "2026-09-02",
    due_date: "2026-10-02",
    currency: "INR",
    subtotal: 8491.53,
    tax_amount: 1528.47,
    total_amount: 10020.0,
    category: "Office Supplies",
    po_number: null,
    description: "Office supplies batch 2",
    decision: {
      decision: "needs_review",
      confidence: 0.65,
      pass_resolved_in: 2,
      exception_type: "fuzzy_duplicate",
      primary_reason: "Probable duplicate of INV-0987 (94% similar)",
      matched_record: "INV-0987",
      violations: [
        {
          rule_id: "R09",
          name: "Fuzzy duplicate",
          severity: "soft",
          penalty: 0.35,
          exception_type: "fuzzy_duplicate",
          message: "Probable duplicate of INV-0987 (94% similar)",
          matched_record: "INV-0987",
          evidence: { vendor_similarity: 1.0, invoice_number_similarity: 0.9, combined_similarity: 0.94 }
        }
      ],
      evidence: { matched_invoice_id: "INV-0987" },
      ai_summary: "Invoice INV-1041 is similar to INV-0987. Verify whether this is a duplicate order.",
      ai_suggested_action: "investigate",
      ai_summary_status: "ready",
      review_status: "pending"
    },
    reviews: []
  },
  {
    id: 5,
    upload_id: 1,
    invoice_id: "INV-1020",
    invoice_number: "GL/2026/0089",
    vendor_name: "Global Logistics Corp",
    invoice_date: "2026-09-01",
    due_date: "2026-10-01",
    currency: "INR",
    subtotal: 122881.36,
    tax_amount: 22118.64,
    total_amount: 145000.0,
    category: "Logistics",
    po_number: "PO-9923",
    description: "Freight and container shipping",
    decision: {
      decision: "needs_review",
      confidence: 0.80,
      pass_resolved_in: 1,
      exception_type: "policy_limit",
      primary_reason: "Total amount exceeds policy limit of 100,000 INR",
      matched_record: null,
      violations: [
        {
          rule_id: "R07",
          name: "Over policy limit",
          severity: "soft",
          penalty: 0.20,
          exception_type: "policy_limit",
          message: "Total amount ₹145,000.00 exceeds policy threshold ₹100,000.00",
          matched_record: null,
          evidence: { policy_limit: 100000, total_amount: 145000 }
        }
      ],
      evidence: {},
      ai_summary: "Invoice exceeds policy limit of ₹100,000. Approved by reviewer based on PO-9923.",
      ai_suggested_action: "approve",
      ai_summary_status: "ready",
      review_status: "approved"
    },
    reviews: [
      {
        id: 1,
        reviewer: "Shree",
        action: "approve",
        comment: "Verified PO-9923 and executive sign-off for large order",
        reviewed_at: "2026-10-07T10:15:00Z"
      }
    ]
  },
  {
    id: 4,
    upload_id: 1,
    invoice_id: "INV-1015",
    invoice_number: "TECH/9912",
    vendor_name: "TechSolutions Inc",
    invoice_date: "2026-10-15",
    due_date: "2026-11-15",
    currency: "INR",
    subtotal: 38135.59,
    tax_amount: 6864.41,
    total_amount: 45000.0,
    category: "IT Equipment",
    po_number: "PO-7701",
    description: "Laptops and peripherals",
    decision: {
      decision: "exception",
      confidence: 0.30,
      pass_resolved_in: 1,
      exception_type: "future_date",
      primary_reason: "Invoice date 2026-10-15 is after as_of_date 2026-10-01",
      matched_record: null,
      violations: [
        {
          rule_id: "R04",
          name: "Future-dated invoice",
          severity: "soft",
          penalty: 0.30,
          exception_type: "future_date",
          message: "Invoice date 2026-10-15 is in the future",
          matched_record: null,
          evidence: { invoice_date: "2026-10-15", as_of_date: "2026-10-01" }
        },
        {
          rule_id: "R01",
          name: "Missing required field",
          severity: "hard",
          penalty: 0.50,
          exception_type: "missing_field",
          message: "Missing vendor tax registration ID",
          matched_record: null,
          evidence: {}
        }
      ],
      evidence: {},
      ai_summary: "Future dated invoice rejected by reviewer.",
      ai_suggested_action: "contact_vendor",
      ai_summary_status: "ready",
      review_status: "rejected"
    },
    reviews: [
      {
        id: 2,
        reviewer: "Shree",
        action: "reject",
        comment: "Future-dated invoice cannot be posted yet",
        reviewed_at: "2026-10-07T10:20:00Z"
      }
    ]
  },
  {
    id: 3,
    upload_id: 1,
    invoice_id: "INV-1008",
    invoice_number: "UB/2026/012",
    vendor_name: "Utility Board",
    invoice_date: "2026-09-04",
    due_date: "2026-09-24",
    currency: "INR",
    subtotal: 28000.0,
    tax_amount: 5040.0,
    total_amount: 32000.0,
    category: "Utilities",
    po_number: null,
    description: "Electricity charges for Sept 2026",
    decision: {
      decision: "exception",
      confidence: 0.15,
      pass_resolved_in: 1,
      exception_type: "calculation_mismatch",
      primary_reason: "Subtotal + Tax differs from Total amount by 4.2%",
      matched_record: null,
      violations: [
        {
          rule_id: "R05",
          name: "Calculation mismatch",
          severity: "soft",
          penalty: 0.35,
          exception_type: "calculation_mismatch",
          message: "Subtotal (28000) + Tax (5040) = 33040, which differs from Total (32000)",
          matched_record: null,
          evidence: { subtotal: 28000, tax_amount: 5040, total_amount: 32000, difference_pct: 4.2 }
        }
      ],
      evidence: {},
      ai_summary: "Calculation mismatch detected: Subtotal + Tax is 33,040 but Total states 32,000. Contact vendor for corrected invoice.",
      ai_suggested_action: "contact_vendor",
      ai_summary_status: "ready",
      review_status: "pending"
    },
    reviews: []
  }
];

export const initialMockAuditLogs = [
  {
    id: 6,
    timestamp: "2026-10-07T10:15:00Z",
    actor: "Shree",
    actor_type: "user",
    event_type: "REVIEW_APPROVED",
    invoice_id: "INV-1020",
    upload_id: 1,
    details: {
      action: "approve",
      comment: "Verified PO-9923 and executive sign-off for large order",
      previous_confidence: 0.80
    }
  },
  {
    id: 5,
    timestamp: "2026-10-07T10:12:00Z",
    actor: "ai-assistant",
    actor_type: "ai",
    event_type: "CHAT_QUERY",
    invoice_id: "INV-1042",
    upload_id: 1,
    details: {
      query: "Why was INV-1042 flagged?",
      tools_used: ["explain_decision"]
    }
  },
  {
    id: 4,
    timestamp: "2026-10-07T10:10:00Z",
    actor: "ai-assistant",
    actor_type: "ai",
    event_type: "AI_SUMMARY_GENERATED",
    invoice_id: "INV-1042",
    upload_id: 1,
    details: {
      suggested_action: "investigate",
      referenced_rules: ["R09", "R10"]
    }
  },
  {
    id: 3,
    timestamp: "2026-10-07T10:05:01Z",
    actor: "decision-engine",
    actor_type: "engine",
    event_type: "INVOICE_FLAGGED",
    invoice_id: "INV-1042",
    upload_id: 1,
    details: {
      decision: "needs_review",
      confidence: 0.50,
      exception_type: "fuzzy_duplicate",
      primary_reason: "Probable duplicate of INV-0987 (96% similar)"
    }
  },
  {
    id: 2,
    timestamp: "2026-10-07T10:05:00Z",
    actor: "decision-engine",
    actor_type: "engine",
    event_type: "INGESTION_COMPLETED",
    invoice_id: null,
    upload_id: 1,
    details: {
      total: 1000,
      auto_pass: 816,
      needs_review: 90,
      exception: 94
    }
  },
  {
    id: 1,
    timestamp: "2026-10-07T10:04:55Z",
    actor: "system",
    actor_type: "system",
    event_type: "UPLOAD_RECEIVED",
    invoice_id: null,
    upload_id: 1,
    details: {
      filename: "invoices_demo.csv",
      size_bytes: 104200
    }
  }
];

export const initialMockConfig = {
  auto_pass_threshold: 0.85,
  exception_below: 0.40,
  policy_limit: 100000,
  rules: [
    { rule_id: "R01", name: "Missing required field", severity: "hard", penalty: 0.50, enabled: true, exception_type: "missing_field" },
    { rule_id: "R02", name: "Invalid amount", severity: "hard", penalty: 0.60, enabled: true, exception_type: "invalid_amount" },
    { rule_id: "R03", name: "Invalid date format", severity: "hard", penalty: 0.40, enabled: true, exception_type: "invalid_date" },
    { rule_id: "R04", name: "Future-dated invoice", severity: "soft", penalty: 0.30, enabled: true, exception_type: "future_date" },
    { rule_id: "R05", name: "Calculation mismatch", severity: "soft", penalty: 0.35, enabled: true, exception_type: "calculation_mismatch" },
    { rule_id: "R06", name: "Exact duplicate", severity: "hard", penalty: 0.80, enabled: true, exception_type: "exact_duplicate" },
    { rule_id: "R07", name: "Over policy limit", severity: "soft", penalty: 0.20, enabled: true, exception_type: "policy_limit" },
    { rule_id: "R08", name: "Unknown vendor or category", severity: "soft", penalty: 0.20, enabled: true, exception_type: "unknown_vendor" },
    { rule_id: "R09", name: "Fuzzy duplicate candidate", severity: "soft", penalty: 0.35, enabled: true, exception_type: "fuzzy_duplicate" },
    { rule_id: "R10", name: "Near-identical amount match", severity: "soft", penalty: 0.15, enabled: true, exception_type: "fuzzy_duplicate" },
    { rule_id: "R11", name: "Historical amount outlier", severity: "soft", penalty: 0.20, enabled: true, exception_type: "amount_outlier" }
  ]
};
