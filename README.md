# Clawproof Checks

**Open-source reliability and governance checks for AI agents.**

Ten opinionated checks. One checklist per check. One verification pass your agent either passes, partially passes, or fails. No theory, no tooling lock-in, no vendor dependency. Built from running agents in production every day.

→ Full writeups: [goclawproof.com/checks](https://goclawproof.com/checks)
→ Interactive assessment: [goclawproof.com/assessment](https://goclawproof.com/assessment)

---

## The 10 Checks

| # | Check | Category |
|---|-------|----------|
| 01 | [Tool Permissions & Least Privilege](checks/01-tool-permissions.yaml) | Security |
| 02 | [Logging & Audit Trails](checks/02-logging-audit-trails.yaml) | Quality |
| 03 | [Prompt Injection & Data Exfiltration](checks/03-prompt-injection.yaml) | Security |
| 04 | [Human-in-the-Loop & Escalation](checks/04-human-in-the-loop.yaml) | Governance |
| 05 | [Rollback & Kill Switches](checks/05-rollback-kill-switches.yaml) | Operations |
| 06 | [Secrets Management](checks/06-secrets-management.yaml) | Security |
| 07 | [Evaluation & Regression Testing](checks/07-evaluation-testing.yaml) | Quality |
| 08 | [Data Boundaries & RAG Governance](checks/08-data-boundaries.yaml) | Governance |
| 09 | [Cost Controls & Rate Limiting](checks/09-cost-controls.yaml) | Operations |
| 10 | [Multi-Agent Coordination](checks/10-multi-agent-coordination.yaml) | Quality |

Each check is a single YAML file with the failure mode, two verification questions, a production checklist, common pitfalls, and a link to the full writeup.

---

## Use it as a Claude skill

A packaged skill is included at [`skills/clawproof-audit/`](skills/clawproof-audit/). Drop it into any Claude Code or Claude Agent SDK project and an agent can audit a codebase, runbook, or configuration against all 10 checks on demand.

```bash
# Clone into your project's skills directory
git clone https://github.com/lexbeam-software/clawproof-checks.git /tmp/clawproof
cp -r /tmp/clawproof/skills/clawproof-audit ./.claude/skills/

# In Claude Code:
> /skills
# Select: clawproof-audit
> audit this agent for production readiness
```

The skill produces a scored audit report (0-100) with prioritized remediation, linked back to the full check writeups.

---

## Use it programmatically

Every check is also bundled into a single JSON file for programmatic consumption:

```bash
curl -O https://raw.githubusercontent.com/lexbeam-software/clawproof-checks/main/skills/clawproof-audit/checks.json
```

Schema: see [`checks/SCHEMA.md`](checks/SCHEMA.md).

---

## Use it as a yardstick

Teams also treat the checks as a pre-production gate. Add them to your agent release checklist; fail a launch if any check scores below 7/10. The YAML is stable enough to diff in CI.

---

## Why an open-source layer?

Because agent governance that only lives inside one consultancy's deck is not governance, it is slideware. These checks are the inputs I wish I had when I started running agents in production. If they save someone a Monday morning incident, the repo has paid for itself.

---

## Contributing

New failure modes, additional checklist items, language-specific playbooks — all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT. Use these checks in commercial products, internal tooling, client deliverables, or anywhere else. Attribution is appreciated but not required.

---

Maintained by [Werner Plutat](https://www.linkedin.com/in/wplu/) / [Lexbeam Software](https://lexbeam.com).

For enterprise rollout support in DACH: [agentklar.de](https://agentklar.de).
