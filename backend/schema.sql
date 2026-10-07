CREATE TABLE IF NOT EXISTS uploads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  uploaded_at TEXT NOT NULL,
  uploaded_by TEXT,
  total_rows INTEGER,
  auto_pass_count INTEGER,
  needs_review_count INTEGER,
  exception_count INTEGER,
  used_history INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  upload_id INTEGER NOT NULL REFERENCES uploads(id),
  invoice_id TEXT NOT NULL,
  invoice_number TEXT,
  vendor_name TEXT,
  invoice_date TEXT,
  due_date TEXT,
  currency TEXT,
  subtotal REAL,
  tax_amount REAL,
  total_amount REAL,
  category TEXT,
  po_number TEXT,
  description TEXT,
  UNIQUE(upload_id, invoice_id)
);

CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_pk INTEGER NOT NULL UNIQUE REFERENCES invoices(id),
  decision TEXT NOT NULL,
  confidence REAL NOT NULL,
  pass_resolved_in INTEGER,
  exception_type TEXT,
  primary_reason TEXT,
  matched_record TEXT,
  violations_json TEXT,
  evidence_json TEXT,
  ai_summary TEXT,
  ai_suggested_action TEXT,
  ai_summary_status TEXT DEFAULT 'not_generated',
  review_status TEXT NOT NULL DEFAULT 'pending',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_pk INTEGER NOT NULL REFERENCES decisions(id),
  reviewer TEXT NOT NULL,
  action TEXT NOT NULL,
  comment TEXT,
  reviewed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  actor TEXT NOT NULL,
  actor_type TEXT NOT NULL,
  event_type TEXT NOT NULL,
  invoice_id TEXT,
  upload_id INTEGER,
  details_json TEXT
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_inv_upload ON invoices(upload_id);
CREATE INDEX IF NOT EXISTS idx_dec_decision ON decisions(decision);
CREATE INDEX IF NOT EXISTS idx_audit_inv ON audit_log(invoice_id);
