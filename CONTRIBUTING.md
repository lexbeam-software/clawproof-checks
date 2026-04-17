# Contributing to Clawproof Checks

Contributions welcome. The bar is: does this check come from a real failure mode someone actually saw in production, and does the verification question have a clear yes/no/partial answer?

## What's welcome

- **Refinements to existing checks.** Sharper wording, better pitfalls, additional checklist items.
- **Platform-specific notes.** If a check behaves differently on OpenAI vs. Anthropic vs. LangChain vs. a custom stack, document it.
- **New checks.** We cap at 10 on purpose. For now, new checks are merged only if they replace an existing one or fork a check that has grown too broad. Open an issue first to discuss.
- **Language-specific playbooks.** Reference implementations of a check in Python, TypeScript, Go, etc.
- **Translations.** English is primary. Quality German, French, Spanish translations welcome.

## What's out of scope

- Vendor-specific marketing content.
- Checks that only apply to a single framework or closed platform.
- Theoretical checks that have never caused a production incident.

## Schema

Every YAML check must validate against [`checks/SCHEMA.md`](checks/SCHEMA.md). CI runs the validator on every PR.

## Attribution

If a check is improved based on a real incident you experienced (anonymized is fine), credit in the commit message or PR description helps the community see the operator-to-operator lineage.

## Questions

Open an issue. For private disclosure (e.g., incident reports you don't want public yet), email contact@lexbeam.com.
