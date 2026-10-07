# Evaluation Report: `invoices_train.csv`

**Date:** 2026-10-07 | **Status:** **PASS (Meets contract targets)**

## 1. Executive Summary & KPIs

| Metric | Target | Result | Status |
|---|---|---|---|
| **Recall (Sensitivity)** | ≥ 0.950 | **97.8%** | ✅ |
| **Precision (PPV)** | ≥ 0.800 | **100.0%** | ✅ |
| **F1 Score** | Balanced | **0.9890** | ✅ |
| **Type Accuracy** | Diagnostic | **93.9%** | ✅ |
| **Overall Accuracy** | System | **99.6%** | ✅ |
| **Specificity** | Clean Pass | **100.0%** | ✅ |

## 2. Confusion Matrix

| | Actually Bad (184) | Actually Clean (816) | Total |
|---|---|---|---|
| **Flagged (Needs Review / Exception)** | **TP: 180** | **FP: 0** | 180 |
| **Auto-Passed** | **FN: 4** | **TN: 816** | 820 |
| **Total** | 184 | 816 | 1000 |

## 3. Decision Breakdown

- **Total Rows:** 1000
- **Auto-Passed (`auto_pass`):** 820 (82.0%)
- **Needs Review (`needs_review`):** 93 (9.3%)
- **Exceptions (`exception`):** 87 (8.7%)

## 4. Per-Exception-Type Diagnostics

| Exception Type | Total Ground Truth | Correctly Flagged | Missed | Type Recall | Diagnosis Accuracy |
|---|---|---|---|---|---|
| `amount_outlier` | 7 | 3 | 4 | 42.9% | 100.0% |
| `calculation_mismatch` | 25 | 25 | 0 | 100.0% | 100.0% |
| `exact_duplicate` | 40 | 40 | 0 | 100.0% | 100.0% |
| `future_date` | 10 | 10 | 0 | 100.0% | 100.0% |
| `fuzzy_duplicate` | 30 | 30 | 0 | 100.0% | 100.0% |
| `invalid_amount` | 12 | 12 | 0 | 100.0% | 100.0% |
| `invalid_date` | 5 | 5 | 0 | 100.0% | 0.0% |
| `missing_field` | 30 | 30 | 0 | 100.0% | 80.0% |
| `policy_limit` | 15 | 15 | 0 | 100.0% | 100.0% |
| `unknown_vendor` | 10 | 10 | 0 | 100.0% | 100.0% |

## 5. False Alarms (False Positives)

**Count:** 0
None (Zero false alarms on clean invoices).

## 6. Missed Invoices (False Negatives)

**Count:** 4
`INV-0999, INV-0994, INV-0998, INV-0995`