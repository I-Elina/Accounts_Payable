# Judge & Evaluator Q&A Preparation Guide

This guide equips the team to answer technical, architectural, and business questions during judging rounds.

---

## 1. Architectural & Algorithmic Questions

### Q1: "Why don't you use an LLM or ML classifier to decide whether an invoice is an exception?"
**Answer:**
> *"Financial compliance and accounting regulations (e.g. SOX, GST audits) require absolute determinism and explainability. If an LLM decides routing, hallucinations or non-deterministic temperature shifts could approve fraudulent invoices or stall critical supplier payments. In our architecture:*
> - *Deterministic rules (R01–R11) make 100% of the routing decisions.*
> - *The LLM only receives structured violations, records, and evidence to synthesize human-readable summaries.*
> - *The LLM has zero execution privileges in the routing loop."*

### Q2: "Why does the decision engine use a 2-Pass architecture?"
**Answer:**
> *"A single pass cannot reliably catch cross-invoice fraud or statistical anomalies:*
> - *Pass 1 validates row-level intrinsic integrity: required fields, numeric formats, valid calendar dates, and GST math calculations.*
> - *Pass 2 performs global batch analytics: pairwise RapidFuzz string distance on vendor names for fuzzy duplicate detection, exact duplicate grouping, and vendor-level mean outlier detection (R11).*
> *This separation ensures single-row checks are $O(N)$ and complex cross-record comparisons run efficiently only on valid candidate records."*

### Q3: "How did you arrive at the 0.85 auto-pass threshold?"
**Answer:**
> *"We executed an empirical threshold sweep across `[0.70, 0.75, 0.80, 0.85, 0.90, 0.95]` on our training dataset (1,000 rows, Seed 42). At 0.85:*
> - *Precision reached 100.0% with 0 false alarms on clean invoices.*
> - *Recall reached 98.4% on our held-out test set (Seed 99), far exceeding the Hackathon benchmark of ≥ 95.0%.*
> - *It creates a clear safety margin: clean invoices score 1.00; mild policy limits or single minor math discrepancies score 0.70–0.80, safely landing in `needs_review`; and critical duplications or missing required fields score 0.00–0.50, routing directly to `exception`."*

---

## 2. Competitive Differentiation

### Q4: "How does this compare to Microsoft Dynamics 365 Finance or SAP Concur?"
**Answer:**
> *"Modern enterprise ERPs offer point solutions, but lack our unified conversational workflow:*
> 1. **Microsoft Dynamics 365 Finance:** Offers Copilot chat and AI confidence scores on OCR extraction fields (e.g., 'Was this vendor name recognized with 92% confidence?'). However, it does not provide confidence breakdowns on the *routing decision itself*, nor does it explain cross-system duplicate anomalies in conversational cards.
> 2. **SAP Concur Invoice / SAP Joule:** Joule acts as a general assistant for expense submissions, but AP exception resolution is still handled through rigid, tabular exception codes without evidence-grounded conversational reasoning.
> 3. **SAP Business ByDesign:** Uses static tolerance limits with hard thresholds, but lacks fuzzy string reconciliation and conversational proposal guardrails.
> 
> *Our system differs by providing: (a) evidence-grounded chat grounded in real violations, (b) transparent mathematical score deductions (1.00 $\rightarrow$ 0.50), and (c) strict proposal-first human approval."*

---

## 3. Product Security & Guardrails

### Q5: "Can the AI hallucinate an approval or take unauthorized actions?"
**Answer:**
> *"No. The chat system is strictly proposal-based:*
> 1. *When a user types 'Approve INV-1042', the backend generates a `proposal` card with a structured payload (`action: "approve"`, `invoice_id: "INV-1042"`).*
> 2. *The database is completely untouched.*
> 3. *Only when an authenticated human clicks the UI 'Confirm' button is a separate POST `/api/invoices/{id}/review` executed, which appends an immutable entry to the SHA-256 audit log."*

### Q6: "How do you protect against CSV formula injection (CSV Injection / DDE attacks)?"
**Answer:**
> *"When exporting exception reports, untrusted inputs (such as malicious vendor names like `=cmd|' /C calc'!A0` or `@SUM(...)`) can execute commands when opened in Microsoft Excel. Our export engine runs sanitization that escapes any field starting with `=`, `@`, `+`, or `-` by prefixing a single quote (`'`), neutralizing any spreadsheet macro execution."*

---

## 4. Honest Limitations & Future Roadmap

### Q7: "What are the limitations of the current prototype?"
**Answer:**
> *"We believe in transparent engineering:*
> 1. **Synthetic Data Baseline:** While our dataset generator accurately models log-normal invoice distributions, Indian GST rates, and SROIE receipt formats, production deployments must handle noisy OCR text from scanned physical paper.
> 2. **Reviewer Identity:** In this hackathon build, reviewer names are submitted via client session state; production systems must bind to Azure Active Directory / Entra ID OAuth tokens.
> 3. **Batch vs Streaming:** Current duplicate detection runs across uploaded batches; an enterprise deployment would query an ongoing ledger database with distributed vector or fuzzy search indices."*
