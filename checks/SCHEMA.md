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
  - question: string
    weight: 5
  - question: string
    weight: 5
checklist:                      # 4-8 items, each actionable
  - string
common_pitfalls:                # exactly 3 entries
  - string
related:                        # 0-4 slugs, all must resolve to an existing check
  - string
site_url: string                # https://goclawproof.com/checks/<slug>
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
| 0-30 | High risk | Do not ship to production |
| 31-60 | Needs work | Significant gaps before production |
| 61-80 | Production-ready with caveats | Address top 3 findings |
| 81-100 | Exemplary | Continuous improvement only |
