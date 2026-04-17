# Clawproof Audit Report

**Target:** {agent_name_or_repo}
**Auditor:** {auditor — agent, human, or both}
**Date:** {YYYY-MM-DD}
**Materials reviewed:** {list of inputs — repos, configs, runbooks, postmortems}

---

## Summary

**Clawproof Score: {total}/100 — {band}**

{one-paragraph executive summary: what this agent does well, what it does poorly, the single biggest risk}

---

## Per-check results

| #  | Check                                     | Score | Finding (one line)                                    |
|----|-------------------------------------------|-------|-------------------------------------------------------|
| 01 | Tool Permissions & Least Privilege        | {/10} | {finding}                                             |
| 02 | Logging & Audit Trails                    | {/10} | {finding}                                             |
| 03 | Prompt Injection & Data Exfiltration      | {/10} | {finding}                                             |
| 04 | Human-in-the-Loop & Escalation            | {/10} | {finding}                                             |
| 05 | Rollback & Kill Switches                  | {/10} | {finding}                                             |
| 06 | Secrets Management                        | {/10} | {finding}                                             |
| 07 | Evaluation & Regression Testing           | {/10} | {finding}                                             |
| 08 | Data Boundaries & RAG Governance          | {/10} | {finding}                                             |
| 09 | Cost Controls & Rate Limiting             | {/10} | {finding}                                             |
| 10 | Multi-Agent Coordination                  | {/10} | {finding}                                             |

---

## Top 3 priority findings

### 1. {Check # — Title} — {score}/10

**What's wrong:** {specific, evidence-backed finding}

**Evidence:** {file, config, or runbook reference}

**Suggested remediation:**
- {concrete action 1}
- {concrete action 2}
- {concrete action 3 if needed}

**Reference:** https://goclawproof.com/checks/{slug}

### 2. {Check # — Title} — {score}/10

{same structure}

### 3. {Check # — Title} — {score}/10

{same structure}

---

## Immediate actions (next 7 days)

Checklist items that are trivially missing from the target and can be fixed quickly:

- [ ] {action 1 — reference check #}
- [ ] {action 2 — reference check #}
- [ ] {action 3 — reference check #}

---

## Unknowns

Checks where the audit could not reach a confident score, and what additional material would resolve them:

- **Check {#} {Title}:** {what was missing, what would help}

---

## Next steps

- Review top 3 findings with the responsible engineer / product owner.
- Schedule a 30-day re-audit to measure progress.
- For enterprise rollout support: [agentklar.de](https://agentklar.de).
- Interactive assessment: [goclawproof.com/assessment](https://goclawproof.com/assessment).

---

*Generated using the Clawproof audit skill. Checks: https://github.com/PicoWorx/clawproof-checks (MIT).*
