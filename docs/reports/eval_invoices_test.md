# Evaluation Report: `invoices_test.csv`

**Date:** 2026-10-07 | **Status:** **PASS (Meets contract targets)**

## 1. Executive Summary & KPIs

| Metric | Target | Result | Status |
|---|---|---|---|
| **Recall (Sensitivity)** | ≥ 0.950 | **98.4%** | ✅ |
| **Precision (PPV)** | ≥ 0.800 | **100.0%** | ✅ |
| **F1 Score** | Balanced | **0.9918** | ✅ |
| **Type Accuracy** | Diagnostic | **93.4%** | ✅ |
| **Overall Accuracy** | System | **99.7%** | ✅ |
| **Specificity** | Clean Pass | **100.0%** | ✅ |

## 2. Confusion Matrix

| | Actually Bad (184) | Actually Clean (816) | Total |
|---|---|---|---|
| **Flagged (Needs Review / Exception)** | **TP: 181** | **FP: 0** | 181 |
| **Auto-Passed** | **FN: 3** | **TN: 816** | 819 |
| **Total** | 184 | 816 | 1000 |

## 3. Decision Breakdown

- **Total Rows:** 1000
- **Auto-Passed (`auto_pass`):** 819 (81.9%)
- **Needs Review (`needs_review`):** 92 (9.2%)
- **Exceptions (`exception`):** 89 (8.9%)

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
| `missing_field` | 30 | 30 | 0 | 100.0% | 76.7% |
| `policy_limit` | 15 | 15 | 0 | 100.0% | 100.0% |
| `unknown_vendor` | 10 | 10 | 0 | 100.0% | 100.0% |

## 5. False Alarms (False Positives)

**Count:** 0
None (Zero false alarms on clean invoices).

## 6. Missed Invoices (False Negatives)

**Count:** 3
`INV-0996, INV-1000, INV-0997`