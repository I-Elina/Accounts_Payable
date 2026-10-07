# Engine — Decision Engine for Cache Me If You Can

Deterministic invoice rules engine.  No AI, no randomness — same input always gives the same output.

## Quick start

```python
from engine import run_engine

result = run_engine("invoices.csv")

# With history and config overrides
result = run_engine(
    "invoices.csv",
    history=previous_invoices,     # list of canonical invoice dicts
    config={"auto_pass_threshold": 0.80, "as_of_date": "2026-10-01"},
)
```

## How it works

### Two passes

- **Pass 1** runs on every invoice: required fields, valid amounts/dates, exact duplicates,
  policy limit, approved vendor/category.  Fast and exact.
- **Pass 2** runs only on *uncertain* invoices (soft violations or fuzzy-match candidates):
  fuzzy duplicate detection, near-identical amount check, vendor amount outlier.

### The 11 rules

| ID  | Name                    | Type | Penalty | Pass |
|-----|-------------------------|------|---------|------|
| R01 | Missing field           | hard | 0.50    | 1    |
| R02 | Invalid amount          | hard | 0.60    | 1    |
| R03 | Invalid date            | hard | 0.40    | 1    |
| R04 | Future date             | soft | 0.30    | 1    |
| R05 | Calculation mismatch    | soft | 0.35    | 1    |
| R06 | Exact duplicate         | hard | 0.80    | 1    |
| R07 | Over policy limit       | soft | 0.20    | 1    |
| R08 | Unknown vendor/category | soft | 0.20    | 1    |
| R09 | Fuzzy duplicate         | soft | 0.35/0.20 | 2 |
| R10 | Near-identical amount   | soft | 0.15    | 2    |
| R11 | Amount outlier          | soft | 0.20    | 2    |

### Score and routing

```
confidence = max(0, 1 - sum_of_penalties)

any hard violation          -> exception
confidence >= 0.85          -> auto_pass
0.40 <= confidence < 0.85   -> needs_review
confidence < 0.40           -> exception
```

## Configuration

Override keys via the `config` parameter:
- `auto_pass_threshold` (float 0-1) — default 0.85
- `exception_below` (float 0-1) — default 0.40
- `policy_limit` (number) — default 100,000
- `as_of_date` (YYYY-MM-DD or null for today)
- `rules.Rxx.penalty` (float) — per-rule penalty override
- `rules.Rxx.enabled` (bool) — disable a rule

Full config: `engine/config/default_config.json`

## Adding a new rule

1. Add a function `rXX(rec, ctx) -> Violation | None` to `engine/rules/pass1.py` or `pass2.py`
2. Add the rule ID and default penalty to `config/default_config.json`
3. Add the `exception_type` to the contract enums if new
4. Add the function to `PASS1_RULES` (or call it in `api.py` for Pass 2)
5. Write a test in `engine/tests/`

## Tests

```bash
pytest engine/tests -v
```
