# Sources And Historical Verification

Read [the skill entry point](../SKILL.md) first. This file preserves the original Primary Behaviour References and their historical source-check date. It is a source register, not evidence of fresh verification and not a replacement for project-specific primary-document checks.

## Verification Rule

These references support limited product-behaviour statements, not the architecture's effectiveness. Every behavioural statement drawn from them is dated to the source check below and may have changed: re-read the current pages and re-verify selected versions, support ranges and feature availability during Phase 1 rather than relying on any figure reproduced here. The skill package is complete without consulting a research memo. Follow [Discovery And Planning](discovery-and-planning.md), Section 3 and decision X01, for the required verification records, current compatibility constraints, selected pins and revalidation on resumption. The historical check date is 13 September 2026. Reorganising these files does not update that date or verify their external sources.

## Primary Behaviour References

- [P1] HashiCorp, terraform validate and init command references: `https://developer.hashicorp.com/terraform/cli/commands/validate` and `https://developer.hashicorp.com/terraform/cli/commands/init` — backend-disabled validation setup, dependency installation and readonly locks.
- [P2] HashiCorp, Dependency Lock File: `https://developer.hashicorp.com/terraform/language/files/dependency-lock` — root-scoped provider locking; remote modules need separate exact selection.
- [P3] HashiCorp, Tests: `https://developer.hashicorp.com/terraform/language/tests` — default apply behaviour; excluded from baseline.
- [P4] HashiCorp, Module Composition, Workspaces and remote-state data source: `https://developer.hashicorp.com/terraform/language/modules/develop/composition`; `https://developer.hashicorp.com/terraform/language/state/workspaces`; `https://developer.hashicorp.com/terraform/language/state/remote-state-data`.
- [P5] GitHub, About code owners; About rulesets; Deployments and environments: `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners`; `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets`; `https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments`.
- [P6] GitHub, Secure use, workflow syntax and required checks: `https://docs.github.com/en/actions/reference/security/secure-use`; `https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax`; `https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks`.
- [P7] Maintainer documentation: `https://github.com/actions/checkout`; `https://github.com/rhysd/actionlint/blob/main/docs/usage.md`; `https://github.com/gitleaks/gitleaks`.
- [P8] Agent discovery: `https://developers.openai.com/codex/guides/agents-md/`; `https://code.claude.com/docs/en/memory`; `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions`.
- [P9] GitHub, supported dependency ecosystems and action updates: `https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories`; `https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions`.
- [P10] Git, git-diff reference: `https://git-scm.com/docs/git-diff` — revision comparisons and raw path handling. All behavioural documentation inspected 13 September 2026; no target-project command was executed during preparation of this skill.

## Original Section Map

- Section 1: purpose, scope and non-goals retained in [SKILL.md](../SKILL.md).
- Sections 2, 7 and 8: [Architecture And Contracts](architecture-and-contracts.md).
- Sections 3–6: [Discovery And Planning](discovery-and-planning.md).
- Sections 9–10: [Validation And GitHub](validation-and-github.md).
- Sections 11–14: [Implementation And Acceptance](implementation-and-acceptance.md).
- Primary Behaviour References P1–P10: this file.

The unnumbered invocation, prerequisites, workflow and outputs sections remain in SKILL.md. Original section numbers are retained in the references to keep requirements traceable. A section number in another file must be read with the mapped filename, not treated as a heading in the entry point.
