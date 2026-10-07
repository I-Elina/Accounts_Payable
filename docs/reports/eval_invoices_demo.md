# Evaluation Report: `invoices_demo.csv`

**Date:** 2026-10-07 | **Status:** **PASS (Meets contract targets)**

## 1. Executive Summary & KPIs

| Metric | Target | Result | Status |
|---|---|---|---|
| **Recall (Sensitivity)** | ≥ 0.950 | **98.4%** | ✅ |
| **Precision (PPV)** | ≥ 0.800 | **99.5%** | ✅ |
| **F1 Score** | Balanced | **0.9891** | ✅ |
| **Type Accuracy** | Diagnostic | **91.7%** | ✅ |
| **Overall Accuracy** | System | **99.6%** | ✅ |
| **Specificity** | Clean Pass | **99.9%** | ✅ |

## 2. Confusion Matrix

| | Actually Bad (184) | Actually Clean (816) | Total |
|---|---|---|---|
| **Flagged (Needs Review / Exception)** | **TP: 181** | **FP: 1** | 182 |
| **Auto-Passed** | **FN: 3** | **TN: 815** | 818 |
| **Total** | 184 | 816 | 1000 |

## 3. Decision Breakdown

- **Total Rows:** 1000
- **Auto-Passed (`auto_pass`):** 818 (81.8%)
- **Needs Review (`needs_review`):** 94 (9.4%)
- **Exceptions (`exception`):** 88 (8.8%)

## 4. Per-Exception-Type Diagnostics

| Exception Type | Total Ground Truth | Correctly Flagged | Missed | Type Recall | Diagnosis Accuracy |
|---|---|---|---|---|---|
| `amount_outlier` | 7 | 4 | 3 | 57.1% | 100.0% |
| `calculation_mismatch` | 25 | 25 | 0 | 100.0% | 100.0% |
| `exact_duplicate` | 40 | 40 | 0 | 100.0% | 100.0% |
| `future_date` | 10 | 10 | 0 | 100.0% | 100.0% |
| `fuzzy_duplicate` | 30 | 30 | 0 | 100.0% | 100.0% |
| `invalid_amount` | 12 | 12 | 0 | 100.0% | 100.0% |
| `invalid_date` | 5 | 5 | 0 | 100.0% | 0.0% |
| `missing_field` | 30 | 30 | 0 | 100.0% | 66.7% |
| `policy_limit` | 15 | 15 | 0 | 100.0% | 100.0% |
| `unknown_vendor` | 10 | 10 | 0 | 100.0% | 100.0% |

## 5. False Alarms (False Positives)

**Count:** 1
`INV-0261`

## 6. Missed Invoices (False Negatives)

**Count:** 3
`INV-0999, INV-0995, INV-0996`