# Architecture And Contracts

Read [the skill entry point](../SKILL.md) first. Read this reference during discovery and before resolving architecture, metadata, command and agent-documentation decisions. It preserves original Sections 2, 7 and 8. Approval and operation records are defined in [Discovery And Planning](discovery-and-planning.md), Sections 4–6. Detailed checks are in [Validation And GitHub](validation-and-github.md). Maintenance and acceptance are in [Implementation And Acceptance](implementation-and-acceptance.md), Sections 12–14.

## 2. Fixed Application Monorepo Conventions

FIXED: application packages live under `apps/<app-slug>/`; service-owned Terraform lives under that application's `infra/`. Slugs use lowercase ASCII letters, digits and single hyphens and start with a letter. Application source layout within the package follows the specifically selected framework, recorded as concrete files during the interview. Do not force a framework to use a made-up source layout.

Use this single directory grammar. Angle-bracket names in this skill are defined schema variables, not executable placeholders. Render actual names and omit inapplicable directories in the resolved plan. Do not create empty tiers, example services or unused tool configuration.

```text
AGENTS.md
README.md
CONTRIBUTING.md
.editorconfig
.gitattributes
.gitignore
.gitleaks.toml
apps/<app-slug>/
  README.md
  <concrete application source, package manifests and tests>
  infra/
    README.md
    modules/<service-module>/
      README.md
      main.tf
      variables.tf
      outputs.tf
      versions.tf
      examples/<fixture-name>/
    roots/<unit-slug>/
      README.md
      main.tf
      variables.tf
      outputs.tf
      versions.tf
      providers.tf [only when configured providers are in scope]
      backend.tf [only when exact local preparation is authorised]
      .terraform.lock.hcl [only when this configuration uses external providers]
infra/
  foundations/roots/<unit-slug>/
  foundations/modules/<module-slug>/
  platform/roots/<unit-slug>/
  platform/modules/<module-slug>/
  modules/<cross-service-module>/
packages/<shared-application-package>/
tooling/
  repo.py
  repository.json
  commands.json
  toolchain.lock.json
  tests/test_repo.py
  tests/fixtures/<named data fixture>.json
  prepared/github/ [only selected GitHub files intentionally kept inactive]
docs/
  ARCHITECTURE.md
  DEVELOPMENT.md [generated]
  REPOSITORY_MAP.md [generated]
  runbooks/repository-maintenance.md
  runbooks/validation-failures.md
  setup/<setup-id>/
    decisions.json
    authorisations.json
    implementation-plan.md
    completion.md
.github/
  CODEOWNERS [generated]
  pull_request_template.md
  ISSUE_TEMPLATE/change.md [only if Issues are selected]
  dependabot.yml [only if the updater is selected and activation authorised]
  workflows/ci.yml [only if local placement here is authorised]
```

Rules for the grammar:

- Each `roots/<unit-slug>/` leaf is an independently executable Terraform root. No parent root calls all environment roots. Environment, account and region are explicit metadata fields, not extra directory levels.
- Each `modules/` leaf is reusable source, not a live deployment. `examples/` leaves are fixtures with no deployment identity. Modules have no backend or embedded provider configurations; they declare compatibility and provider requirements. Provider instances and aliases belong to roots or explicit fixture harnesses.
- `infra/foundations` contains organisation/account governance and administrative foundations only where their source is actually owned in this repository. `infra/platform` contains shared infrastructure only when separately justified. An external foundation/platform is represented as an external interface, not copied into the repository.
- `infra/modules` is for cross-service reusable Terraform source. `packages` is only for genuinely shared application code. Do not promote a one-off service module merely to fill a shared folder.
- These are responsibility boundaries, not resource-type rules. A service-specific network can be service-owned; not every resource in an account is a foundation. Applications do not receive authority over foundations or shared platform merely because source is co-located.
- Distinct owners, credentials, change lifecycles and recovery needs justify independent roots/states. A directory does not automatically need state; an application does not automatically need an account. New managed contexts use one root directory per deployment unit, and no CLI-workspace-based production isolation. Existing workspace arrangements are recorded and preserved, not silently migrated.
- In an existing repository, inspect before any move. New in-scope app/infra code uses this grammar. If relocating existing live roots is not authorised, retain their exact paths as legacy-read-only mappings. Report partial architectural adoption; do not label preserved nonconforming live code as fully migrated. Any conflict preventing authorised app/infra co-location requires interview resolution rather than an infrastructure-only substitute.

FIXED promotion rule: local modules are checkout-coupled. Use them only when coordinated source adoption is confirmed. If consumers must remain on different implementations, resolve exact registry versions or immutable Git commit sources per consumer before implementation. Do not install publishing infrastructure in bootstrap. Consume an existing approved release, use a specifically approved whole-source immutable revision model, or exclude that deployable configuration until a separate scope is approved. Whole-source promotion bundles every required input from one retained revision; it is not just a root-file pin. Delaying a production job does not pin a local module. Production and non-production plans would belong to their own states; a development saved plan is never a promotion artefact. This skill does not run those plans.

## 7. Concrete Architecture, Inventory And Ownership

`tooling/repository.json` is the single source of truth for navigation, ownership, classification, source impact and deployment-unit identity. Use UTF-8 JSON, schema_version 1, sorted object keys when generated, two-space indentation and a final newline. Reject duplicate keys, duplicate IDs, unknown fields and invalid types. Author-maintained source files need not be regenerated. The validator is `tooling/repo.py`; tests define the schema contract.

Top-level keys: `schema_version`, `repository`, `owners`, `units`, `external_contracts`, `global_inputs`, `generated_files`, `agent_profiles`, `github`, `maintenance`.

- `repository`: immutable project `id`, GitHub `owner`/`name`, `default_branch`, `setup_scope`, `legacy_read_only_paths`.
- `owners`: map stable owner IDs to named people/teams, verified GitHub handles where applicable, responsibilities and contact channel. Ownership does not confer access rights.
- `units`: array of objects with `id`, `kind`, `path`, `owner_ids`, `source_paths`, `source_dependencies`, `check_command_ids`, `generated_input_ids`, `lifecycle`, `deployment`. Kinds: `app`, `app-package`, `tf-module`, `tf-root`, `fixture`, `automation`, `input`. Paths are repository-relative canonical POSIX paths. source_paths entries are exact file paths or directory prefixes ending in `/`; avoid ambiguous glob semantics. A dependency entry has `unit_id` and `reason`.
- `deployment` is null for every non-root. For tf-root it has `unit_id`, `tier` (application/platform/foundations), `app_id` or null, `environment`, `target` (provider, account/project, region/location), `state` (logical_id, status, backend_type, non_secret_locator, execution_context), `upstream_contract_ids`, `deployment_after`, `credential_references`, `promotion`, `execution_policy`. IDs are immutable. New unit IDs are user-confirmed stable slugs, globally unique within the repository; the immutable repository ID scopes them across repositories. Do not recycle retired IDs.
- State status is `unassigned-nondeployable`, `configured-not-connected`, or `existing-unchanged`. In the first case backend locator/credential references are null with an explicit reason; no deployment commands or backend files may be emitted. For configured/existing state record the exact effective backend/workspace identity. Distinct managed roots must not resolve to the same state. A legacy alias sharing state is recorded as non-executable and escalated, not duplicated as an independent root. Directory renames do not change logical IDs or effective state locators.
- `execution_policy`: allowed command IDs, required execution profile, local preparation status; deployment is explicitly forbidden by this setup. `deployment_after` records operational dependencies, never execution permission.
- `external_contracts`: stable ID, producer and owner, consumers, typed/versioned fields, published value source, freshness/version expectation, permitted read scope, setup representation. Prefer supplied typed values; do not default to reading entire upstream state. Fixture values must be unmistakably non-live and only under fixture paths. A live-looking invented account or resource ID is forbidden.
- `global_inputs`: source paths and affected unit IDs or `all-validation-units`. Include automation, workflow inputs, lock files, templates and relevant policies. Global tools/metadata/workflow changes select all validation units.
- `generated_files`: ID, exact output path, source paths, generator command ID, owner, tracked flag. Outputs have a generated notice and must not be edited directly. Application-generated code and artefacts belong here, not just documentation.
- `agent_profiles`: selected product/surface/version, automatic instruction discovery, bridge paths, scoped loading procedure, verified document/date, smoke-test record and restrictions. No bridge for an unselected agent.
- `github`: desired controls, observed controls, availability evidence, operation IDs, required-check names, CI trigger contract and updater coverage; it is not proof of hosted enforcement.
- `maintenance`: named owners, review cadence, release/no-release policy, licence/distribution resolution and add/retire procedures.

Every tracked package/Terraform directory must classify as a unit, fixture, generated output or explicit preserved legacy path. Parent directories are not automatically units. No executor discovers deployment candidates by recursively running Terraform in every directory. Resolve symlinks and reject paths escaping the repository; reject overlapping executable-root paths, collisions on case-insensitive supported filesystems, dangling dependencies and cycles in build prerequisites. Source-impact cycles may be conservatively collapsed into a strongly connected component; deployment cycles are unresolved architecture and block deployable configuration.

For each new root, define main.tf as composition; versions.tf as selected CLI/provider constraints; variables.tf and outputs.tf as typed documented interfaces; providers.tf only for resolved provider instances; backend.tf only for fully resolved authorised non-secret local configuration. Set explicit provider target guards when supported by the selected provider and document that they do not confer permission. Do not add lifecycle/provisioner/import/moved/state-migration constructs merely for setup. Module examples are validation fixtures, not operational roots. Do not create empty lock files for provider-free contracts.

## 8. Agent Documentation And Command Contracts

The root AGENTS.md is canonical. Keep it concise enough for selected agents' limits; do not impose an unsupported magic line count. It must contain these rules, with actual project identifiers and document links substituted:

```text
This repository contains the applications and service-owned Terraform listed in docs/REPOSITORY_MAP.md.
Read the approved project setup/scope record and this file before changing anything; inspect scoped instructions for each edited path.
Use tooling/repository.json for ownership, classification and dependencies, and tooling/commands.json for executable command contracts. docs/DEVELOPMENT.md is their generated human-readable guide.
Do not edit generated outputs directly. Change their declared source and run the named generator only when authorised.
Repository edits, downloaded-code execution, remote GitHub changes and cloud/state operations are separate permissions. Credentials and green checks do not grant permission.
Do not run deployment, state mutation, credentialled plan/test, privileged untrusted code, or change live deployment controls as repository setup.
Do not overwrite user work, silently change state identity, loosen protections, or treat a skipped/blocked check as passed.
Update dependency/ownership metadata and affected documentation in the same change as their source.
When facts, authority or required behaviour conflict with the approved plan, stop affected work and invoke deep-interview one question at a time. Unresolved critical decisions cannot be bypassed by scores or round limits.
Report exact checks executed and exclusions; distinguish prepared source from deployed infrastructure.
```

Add only necessary local rules in scoped AGENTS.md files at an app/module/root or authority boundary. In-repository precedence: scoped rules add detail and may tighten restrictions; they cannot relax root safety/authority. A conflicting instruction triggers a stop. External system/organisation/user instructions still apply; repository files are not a means of overriding them. Metadata defines commands; do not duplicate command flags in prose.

Selected-agent discovery is a project decision, not an assumption that all agents read AGENTS.md. Verify actual product and surface. Codex documentation describes startup discovery from the Git root to its current directory, override files and a size limit; explicitly read deeper scoped instructions before editing when they were not auto-loaded. Claude Code documentation describes CLAUDE.md and supports an `@AGENTS.md` import: if selected, use a minimal root CLAUDE.md import and scoped imports where required, not copied rules. GitHub Copilot support differs by surface: verify the selected surface's instruction matrix; generate a narrow supported bridge only if needed and test it. For any bridge, repository.json records its generator or exact import and drift checking. Never install agents, skills, extensions or user-global settings just to make the file discoverable. A selected agent unable to load required instructions must be explicitly instructed to read them and that path must be verified, or it is not approved for autonomous implementation.

Required human documents:

- README.md: actual purpose, initial app state, concise navigation entry, ownership, how to reach the command guide and setup record; state whether anything is connected/deployed. No duplicate long command list.
- CONTRIBUTING.md: change/review process, metadata/docs update rule, licence/distribution policy, check result semantics, no auto-merge, and authority boundaries.
- docs/ARCHITECTURE.md: one initial decision record covering co-location, state/authority boundaries, source/deployment graphs, interfaces and promotion. Add dated decisions only for actual changes.
- docs/DEVELOPMENT.md: generated command contracts and platform prerequisites from commands.json and toolchain.lock.json, with the generator version/hash in the header.
- docs/REPOSITORY_MAP.md: generated owners, concrete unit tree, root/state/target maps, external contracts, generated files and agent-entry map.
- runbooks/repository-maintenance.md: exact add/retire/update/drift procedures in implementation-and-acceptance.md, Section 13. runbooks/validation-failures.md: distinguish source failure, missing dependency, blocked permission, malformed output and required escalation; no live “repair” commands.
- App/module/root README files contain only genuinely local purpose, interface and classification, linking to canonical commands rather than duplicating them.

`tooling/commands.json` schema: top-level `schema_version`, `commands`, `execution_profiles`. Every command entry has `id`, `unit_ids`, `description`, `cwd`, `argv`, `tool_ids`, `prerequisites`, `inputs`, `outputs`, `side_effects`, `network`, `credential_class`, `execution_profile`, `timeout_seconds`, `allowed_operation_ids`, `success`, `failure`, `mutates_source`, `ci_required`, `maintenance_owner`. Array argv, never a shell-interpreted string. No arbitrary extra arguments from PRs, unit IDs or filenames. Any typed runtime inputs have an explicit source, allowed values/format and binding algorithm. A concrete implementation plan expands the selected command for each unit; no unbound working directory.

FIXED command entry point: the resolved Python executable runs `tooling/repo.py` from the repository root. The plan records its exact executable name/path per supported platform, rather than assuming `python` and `python3` are interchangeable. Subcommands:

- `doctor`: verify root, metadata, pins and installed binary versions; no installation, network, cloud auth, or implicit fix.
- `inventory --check`: validate schema/classification/IDs/paths/ownership/dependencies and authoritative before/after state-identity mappings.
- `select --base <validated-commit> --head <validated-commit>`: emit impact JSON with selected IDs, reasons, deleted IDs and fallback reason; no checkout, fetch, code execution or deployment. Argument names here denote declared runtime inputs only.
- `generate --check` or `generate --write`: deterministically compare/write only declared generated outputs. Check mode writes temporary bytes outside source and returns failure on drift. Write mode needs explicit local path authority. Neither changes authored HCL or app source.
- `check --unit <registered-id>` and `check --all`: execute only registered bounded checks in approved profiles, preserve per-check evidence, and fail if a required check cannot run. No auto-install or automatic fix.
- `ci`: resolve event revisions, determine expected checks, run checks, and verify final evidence completeness. It has no deployment subcommand.
- `self-test`: run `unittest` for tooling/tests including synthetic selector/safety fixtures. These tests do not call GitHub/cloud APIs.
- `format --unit <registered-id>`: explicitly requested source formatting within approved paths, not a side effect of check.

Exit convention for repo.py: 0 only for completed successful command or genuinely empty impact calculation; 1 verification failure; 2 invalid input/configuration/unsupported version; 3 blocked or missing permission/prerequisite; 4 unexpected execution error. A component marked inapplicable has a documented reason and is not described as passed. Unknown flags, unknown IDs, duplicate metadata keys and malformed tool output fail closed. Timeouts and cancellation are not successes. Log UTC time, commit/tree fingerprint, command ID/argv/cwd, tool identity, input hashes, exit status, output location and redacted summary. Do not print secrets, full environment, tokens, state or plans.
