import labelsData from '../mocks/labels.json';

export const DECISION_LABEL = labelsData.decision || {
  auto_pass: 'Auto-passed',
  needs_review: 'Needs review',
  exception: 'Exception',
};

export const EXCEPTION_LABEL = labelsData.exception_type || {
  none: 'No issue',
  missing_field: 'Missing field',
  invalid_amount: 'Invalid amount',
  invalid_date: 'Invalid date',
  future_date: 'Future-dated',
  calculation_mismatch: 'Calculation mismatch',
  exact_duplicate: 'Exact duplicate',
  fuzzy_duplicate: 'Probable duplicate',
  policy_limit: 'Over policy limit',
  unknown_vendor: 'Unknown vendor/category',
  amount_outlier: 'Unusual amount',
};

export const REVIEW_STATUS_LABEL = labelsData.review_status || {
  not_required: 'Not required',
  pending: 'Pending',
  approved: 'Approved',
  rejected: 'Rejected',
};

export const ACTION_LABEL = labelsData.suggested_action || {
  approve: 'Approve',
  reject: 'Reject',
  investigate: 'Investigate',
  contact_vendor: 'Contact vendor',
};

export const EVENT_LABEL = labelsData.event_type || {
  UPLOAD_RECEIVED: 'File uploaded',
  INGESTION_COMPLETED: 'File processed',
  INVOICE_AUTO_PASSED: 'Auto-passed',
  INVOICE_FLAGGED: 'Sent for review',
  AI_SUMMARY_GENERATED: 'AI summary created',
  REVIEW_APPROVED: 'Approved by reviewer',
  REVIEW_REJECTED: 'Rejected by reviewer',
  SETTINGS_CHANGED: 'Settings changed',
  CHAT_QUERY: 'Assistant question',
};
