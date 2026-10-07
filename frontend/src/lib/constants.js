export const CATEGORIES = [
  'Office Supplies',
  'IT Equipment',
  'Software & Licenses',
  'Travel',
  'Utilities',
  'Professional Services',
  'Marketing',
  'Logistics',
  'Maintenance',
  'Raw Materials',
];

export const DECISIONS = ['auto_pass', 'needs_review', 'exception'];

export const EXCEPTION_TYPES = [
  'none',
  'missing_field',
  'invalid_amount',
  'invalid_date',
  'future_date',
  'calculation_mismatch',
  'exact_duplicate',
  'fuzzy_duplicate',
  'policy_limit',
  'unknown_vendor',
  'amount_outlier',
];

export const REVIEW_STATUSES = ['not_required', 'pending', 'approved', 'rejected'];

export const DEFAULT_THRESHOLDS = {
  auto_pass_threshold: 0.85,
  exception_below: 0.40,
  policy_limit: 100000,
};
