# YAML Schema

Every check in `checks/*.yaml` validates against this schema.

```yaml
id: string                      # "01" through "10", zero-padded
slug: string                    # kebab-case, matches filename stem
title: string                   # human-readable, title case
category: enum                  # Security | Governance | Operations | Quality
tagline: string                 # one-line hook, appears on site cards
failure_mode: string            # 2-3 sentence narrative (block scalar)
verification:                   # exactly 2 entries, each weight 5 -> total 10
  - id: string                  # stable question id, e.g. "01a"
    question: string
    weight: 5
  - question: string
    weight: 5
checklist:                      # 4-8 items, each actionable
  - string
common_pitfalls:                # exactly 3 entries
  - string
related:                        # 0-4 slugs, all must resolve to an existing check
  - string
site_url: string                # https://www.goclawproof.com/checks/<slug>
```

## Scoring convention

- `yes` (5 points) — the verification question is true with evidence in code/config/runbook.
- `partial` (2 points) — the verification question is partially true, or true without evidence.
- `no` (0 points) — the verification question is false.
- `unknown` (0 points) — the auditor cannot determine. Treated as `no` for scoring but noted separately in the report.

Per check max: 10 points. Total across 10 checks: 100 points.

## Score bands

| Score | Band | Meaning |
|-------|------|---------|
| 0-39 | At risk | Basic controls are absent or unverified |
| 40-64 | Foundational | Some controls exist, with material gaps |
| 65-84 | Controlled with gaps | Most controls exist, but the gate may still block or require review |
| 85-100 | Mature controls | Strong coverage; the independent gate decision still applies |

The score describes control coverage. It is not the release decision. The versioned
production gate in [`policy/clawproof-gate.v1.json`](../policy/clawproof-gate.v1.json)
returns `PASS`, `REVIEW`, or `BLOCK`. A critical failed control overrides a high
aggregate score, and missing evidence can never produce `PASS`.
