---
name: clawproof-audit
description: Audit an AI agent codebase, configuration, or runbook against the 10 Clawproof reliability and governance checks. Produces a scored report (0-100) with prioritized remediation findings linked to the full check writeups at goclawproof.com.
---

# Clawproof Audit

## When to use this skill

Use this skill when the user asks any of the following:

- "Audit this agent for production readiness."
- "Is my AI agent safe to ship?"
- "Run a governance or reliability review on this codebase."
- "Score this agent against Clawproof."
- "What are the biggest risks in my agent setup?"

The skill works on any combination of source code, deployment configuration, architecture docs, runbooks, and incident logs the user provides. It does not require the target to be a specific framework or vendor — the checks are framework-agnostic.

## What this skill does

1. Loads the 10 Clawproof checks from `../../checks/*.yaml` (or from the bundled `checks.json` if YAML parsing is unavailable).
2. For each check, examines the target material and answers the two verification questions.
3. Scores each check out of 10 (2 questions × 5 points, partial credit permitted).
4. Produces a report using the template at `templates/audit-report.md`.
5. Surfaces the top 3 lowest-scoring checks as priority findings with links to the full writeups at https://www.goclawproof.com/checks/[slug].

## How to score

For each of the 2 verification questions on each check:

| Answer | Points | When to use |
|---|---|---|
| yes | 5 | The claim is true and there is concrete evidence (code, config, runbook entry) to support it. |
| partial | 2 | The claim is partially true, or true in principle but without enforcement / evidence. |
| no | 0 | The claim is false. |
| unknown | 0 | You cannot determine from the material provided. Note this separately in the report. |

Sum the two questions for a per-check score out of 10. Total across 10 checks = 0-100.

### Score bands

- **0-30: High risk.** Do not ship to production.
- **31-60: Needs work.** Significant gaps. Block release until top findings addressed.
- **61-80: Production-ready with caveats.** Address the top 3 findings before or immediately after release.
- **81-100: Exemplary.** Focus on continuous improvement.

## How to run the audit

**Inputs to request from the user, in order of usefulness:**

1. The agent's source code repo or key files (orchestration, tool definitions, system prompts).
2. Deployment / infrastructure config (environment variables, secret manager setup, permission manifests).
3. Runbooks or incident response docs.
4. Past incident postmortems (the highest-signal input if available).
5. Observability / logging setup.

**Execution order:**

1. Skim the entire codebase first for orientation. Do not start scoring on the first file.
2. Go check by check, in order 01 → 10. For each check:
   - Load the YAML. Read the failure_mode carefully — it frames what you are looking for.
   - Apply the verification questions to the material. Look for evidence, not claims.
   - Assign scores with a one-sentence justification each.
   - Note any checklist items that are obviously missing, for the report's "immediate actions" section.
3. After all 10 checks, sort findings by score ascending. The lowest 3 are the priority remediation targets.
4. Produce the final report using `templates/audit-report.md`. Do not invent content that is not in the YAML or the target codebase.

## Output contract

The final output must include:

- **Total score** out of 100, with score band label.
- **Per-check table** showing check #, title, score, and one-line finding.
- **Top 3 priority findings** with: what's wrong, evidence, 1-3 suggested remediations, link to `https://www.goclawproof.com/checks/[slug]`.
- **Immediate actions** section: any checklist items that are trivially missing and should be fixed in the next 7 days.
- **Unknowns**: any checks where you could not determine a score, with what additional input would help.

## What this skill must NOT do

- **Never invent failure modes or checklist items that are not in the YAML.** If the evidence does not support a finding, score higher and explain why.
- **Never rewrite the user's code.** Audits produce findings and suggestions, not patches. If the user explicitly asks for a fix, that is a separate follow-up.
- **Never score optimistically to be nice.** An honest 45/100 saves an incident; a sycophantic 78/100 costs one.
- **Never skip a check because it feels "not applicable."** If the check does not apply, say so explicitly in the report with the reason — that is itself a useful finding.

## Attribution

Clawproof checks are maintained by Werner Plutat / Lexbeam Software and licensed MIT. Full writeups at [www.goclawproof.com/checks](https://www.goclawproof.com/checks). For enterprise rollout support in DACH, see [www.agentklar.de](https://www.agentklar.de).
