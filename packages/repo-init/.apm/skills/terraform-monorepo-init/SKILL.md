---
name: terraform-monorepo-init
description: Use when a user asks to set up, bootstrap, restructure or extend an application-and-Terraform monorepo, including adding an application, service-owned infrastructure, repository automation, agent documentation or CI safeguards to a new or existing repository. Runs read-only discovery and a mandatory deep-interview, produces a standalone approved implementation plan, and implements only that plan; never provisions cloud infrastructure or performs deployments.
---

# Terraform Monorepo Init

## When To Use This Skill

Invoke this skill when the request concerns the structure, automation or safeguards of a repository holding applications together with their Terraform, whether the repository is new or already exists. Typical triggers: create an application monorepo; add an application or service-owned infrastructure to one; introduce repository metadata, a command runner, agent instructions or dependency-aware CI; or restructure existing application and infrastructure code under one grammar. The intended output is a real application-and-Terraform monorepo, not a template repository.

Do not invoke this skill for cloud provisioning, deployment, state operations or credentialled Terraform runs. Those are excluded from every scope this skill produces and require their own operation-specific plan and approval.

## Prerequisites And Inputs

Before starting, confirm: a target directory or supplied repository context; permission to read it; and the availability of the deep-interview skill. If the repository or the deep-interview skill is inaccessible, report the missing prerequisite and stop. Failed discovery is not evidence of a new repository.

## Workflow Overview

Work through the phases in order and do not begin a later phase until the earlier one has produced its output. Phase 1 is read-only discovery followed by the mandatory deep-interview, resolving the decision schema under the authorisation classes in references/discovery-and-planning.md. Phase 2 generates a standalone implementation plan and obtains explicit approval of an exact revision and operation list. Phase 3 implements only the approved plan. Phase 4 evidences acceptance, idempotency and handover. No implementation starts merely because the interview ends.

## Mandatory Reading Map

This file is the entry point, not the whole skill. Read all five reference files before finalising the standalone plan, and re-read the applicable one before each phase. If a required reference file is missing or unreadable, report the missing prerequisite and stop; do not reconstruct its requirements from memory.

- [references/discovery-and-planning.md](references/discovery-and-planning.md) — read-only discovery, mandatory deep-interview, time-sensitive verification, the decision schema, the authorisation matrix and prohibited operations, and standalone plan generation and approval (original Sections 3 to 6).
- [references/architecture-and-contracts.md](references/architecture-and-contracts.md) — fixed monorepo conventions and directory grammar, repository metadata and ownership, agent documentation and command contracts (original Sections 2, 7 and 8).
- [references/validation-and-github.md](references/validation-and-github.md) — toolchain pinning, application and Terraform checks, secrets and ignore rules, source-impact selection, the GitHub Actions contract, dependency updates and separately authorised GitHub configuration (original Sections 9 and 10).
- [references/implementation-and-acceptance.md](references/implementation-and-acceptance.md) — ordered implementation tasks, acceptance tests AT01 to AT22, idempotency and bounded recovery, completion evidence and handover (original Sections 11 to 14).
- [references/sources.md](references/sources.md) — primary behaviour references P1 to P10 and the historical 13 September 2026 source check, which is provenance only and never current verification.

The generated project plan must reproduce its complete project-specific instructions and may not depend on this skill package being available to its implementation agent.

## Non-Negotiable Gates

These gates apply in full even before the reference files are read, and no reference file, repository instruction, score, round limit or convenience argument relaxes them.

- Read-only discovery and the deep-interview are mandatory and precede questions about discoverable facts. Failed discovery is not evidence of a new repository.
- Discovery, local preparation, remote GitHub changes and cloud/state/deployment are separate authorisation classes. A credential, login, available runner, completed interview or general setup request never implies permission.
- Cloud provisioning, deployment, state operations, credentialled Terraform runs and changes to existing live deployment controls are excluded from every scope this skill produces. They require their own operation-specific plan and approval.
- No write happens before the user approves an exact plan revision and operation list. A materially changed plan needs renewed approval.
- Every version, support ceiling, feature availability and product-behaviour claim in this skill package is a dated observation. Verify it against current primary documentation at this instantiation, and seek renewed approval rather than silently adopting a drifted finding.
- Preserve user work. Never overwrite, reset, clean, stash or force-push over it, and stop for resolution instead.
- Report truthfully: prepared, passed, blocked, excluded and not executed are distinct statuses, and completion evidence must keep them separate.

## Outputs

This skill produces exactly two outputs for each real project: a standalone approved implementation plan at `docs/setup/<setup-id>/implementation-plan.md` with its decision and authorisation records at `docs/setup/<setup-id>/decisions.json` and `docs/setup/<setup-id>/authorisations.json`, and evidence at `docs/setup/<setup-id>/completion.md` of implementing only that plan. Using this skill does not itself create a GitHub repository, cloud account, backend, deployment identity or running service, and it is not authorisation to provision infrastructure.

## Purpose, Scope And Non-Goals

Apply this skill with the available deep-interview skill and read access to the target repository. Its first mandatory phase is read-only discovery followed by deep-interview. The phase produces a complete, project-specific implementation plan and obtains explicit approval. No implementation starts merely because the interview ends.

This skill is a procedure for producing an authorised plan, not itself authorisation and not a command to provision infrastructure. It has two outputs for each real project: a standalone approved implementation plan, then evidence of implementing only that plan. Following this skill does not create a generic template, GitHub repository, cloud account, backend, deployment identity or running service.

Four labels distinguish statements: FIXED is a convention of this skill; DECISION is resolved for the specific project; DEFAULT is a proposed value that requires user confirmation; DOCUMENTED is product behaviour that must be checked against the selected version. A default is not implicit consent. References explain behaviour; the implementation instructions must stand alone.

A resolved exclusion is complete. For example: “Existing remote deployment workflows and settings are outside this setup scope and must remain byte-for-byte/configuration-equivalent unchanged.” “Configure deployment later” is not a resolution.

The baseline is repository preparation and bounded, credential-free validation. Cloud operations and changes to existing live deployment controls are excluded from executable setup tasks. If the user requests them, stop that workstream and require a separate operation-specific plan and approval; do not append them to bootstrap. Local preparation of precise, non-secret configuration may be authorised without activation. Do not treat a workflow with a manual trigger as inert.
