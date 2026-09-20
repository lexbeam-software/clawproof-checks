# Clawproof Checks

**Open-source reliability and governance checks for AI agents.**

Ten opinionated checks plus a deterministic production gate. The coverage score shows where controls are strong or weak. The gate returns `PASS`, `REVIEW`, or `BLOCK` from declared answers and evidence references. No tooling lock-in and no vendor dependency.

→ Full writeups: [www.goclawproof.com/checks](https://www.goclawproof.com/checks)
→ Interactive assessment: [www.goclawproof.com/assessment](https://www.goclawproof.com/assessment)

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

## Run the production gate

The CLI uses Python's standard library and sends nothing over the network. Start with
the example declaration, replace the evidence references with your own, and run it:

```bash
git clone https://github.com/lexbeam-software/clawproof-checks.git
cd clawproof-checks

./bin/clawproof gate examples/gate-pass.json --format markdown --target my-agent
```

Exit codes are stable for CI:

| Exit | Decision | Meaning |
|---:|---|---|
| 0 | `PASS` | Every answer is yes and has evidence |
| 2 | `REVIEW` | A control or evidence reference is incomplete |
| 3 | `BLOCK` | A critical control explicitly failed |
| 4 | `INVALID` | The declaration or selected policy fails structural validation |

The score is diagnostic, not the release decision. A critical failure blocks even at
95/100, and an affirmative claim without an evidence reference cannot produce `PASS`.
The gate does not open or authenticate those references. See the versioned policy at
[`policy/clawproof-gate.v1.json`](policy/clawproof-gate.v1.json) and copy the example
workflow from [`examples/github-actions/clawproof-gate.yml`](examples/github-actions/clawproof-gate.yml).

The gate evaluates what you declare. It does not inspect or certify a production
environment. Evidence references are included in the report for a human or CI process
to verify.

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

Maintained by [Werner Plutat](https://www.linkedin.com/in/wplu/) / [Lexbeam Software](https://www.lexbeam.com).

For enterprise rollout support in DACH: [www.agentklar.de](https://www.agentklar.de).
