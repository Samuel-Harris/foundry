#!/usr/bin/env python3
"""Validate Foundry APM primitives against the contracts APM 0.30.0 does not check.

APM 0.30.0 deploys skill files without validating their frontmatter, so a skill
with a missing `description` installs silently. This script is the structural
gate that closes that gap. It checks, for every package under `packages/`:

  * skills     `.apm/skills/<name>/SKILL.md`          requires name, description
  * agents     `.apm/agents/<name>.agent.md`           requires description
  * instructions `.apm/instructions/<name>.instructions.md` requires description, applyTo

and additionally:

  * the frontmatter parses as YAML (an unquoted `: ` silently corrupts it);
  * a skill's `name` equals its directory name and matches the APM name grammar;
  * `description` is non-empty and at most 1024 characters;
  * every relative markdown link inside a primitive resolves on disk, so the
    `references/` and `scripts/` files a skill promises are actually shipped;
  * nothing escapes the three globs above: a `foo.md` agent, a `foo.md`
    instruction or a skill directory with no `SKILL.md` fails here instead of
    passing unnoticed.

Exit status is 0 when everything passes, 1 when any check fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages"

NAME_GRAMMAR = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")

PRIMITIVE_CONTRACTS = (
    (".apm/skills/*/SKILL.md", "skill", ("name", "description")),
    (".apm/agents/*.agent.md", "agent", ("description",)),
    (".apm/instructions/*.instructions.md", "instruction", ("description", "applyTo")),
)

UNCLASSIFIED_GLOBS = (
    (".apm/agents/*.md", ".agent.md", "agent"),
    (".apm/instructions/*.md", ".instructions.md", "instruction"),
)


def check_discovery(failures: list[str]) -> None:
    for package_dir in sorted(PACKAGES_DIR.iterdir()):
        if not package_dir.is_dir():
            continue
        for pattern, suffix, kind in UNCLASSIFIED_GLOBS:
            for path in sorted(package_dir.glob(pattern)):
                if not path.name.endswith(suffix):
                    failures.append(f"{path}: {kind} files must be named *{suffix}")
        for skill_dir in sorted(package_dir.glob(".apm/skills/*")):
            if skill_dir.is_dir() and not (skill_dir / "SKILL.md").is_file():
                failures.append(f"{skill_dir}: skill directory has no SKILL.md")


def split_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else None


def check_links(path: Path, text: str, failures: list[str]) -> None:
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for target in LINK_PATTERN.findall(body):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0].strip()
        if not relative:
            continue
        if not (path.parent / relative).exists():
            failures.append(f"{path}: dangling link -> {target}")


def check_primitive(path: Path, kind: str, required: tuple[str, ...], failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    raw = split_frontmatter(text)
    if raw is None:
        failures.append(f"{path}: no YAML frontmatter block")
        return
    try:
        metadata = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        detail = str(error).splitlines()[0]
        failures.append(f"{path}: frontmatter is not valid YAML ({detail})")
        return
    if not isinstance(metadata, dict):
        failures.append(f"{path}: frontmatter is not a mapping")
        return

    for field in required:
        value = metadata.get(field)
        if value is None or not str(value).strip():
            failures.append(f"{path}: missing required field '{field}'")

    description = str(metadata.get("description") or "")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        failures.append(
            f"{path}: description is {len(description)} characters, limit is {MAX_DESCRIPTION_LENGTH}"
        )

    if kind == "skill":
        name = str(metadata.get("name") or "")
        if name and name != path.parent.name:
            failures.append(f"{path}: name '{name}' does not match directory '{path.parent.name}'")
        if name and not NAME_GRAMMAR.match(name):
            failures.append(f"{path}: name '{name}' breaks the APM name grammar")
        if len(name) > MAX_NAME_LENGTH:
            failures.append(f"{path}: name is {len(name)} characters, limit is {MAX_NAME_LENGTH}")

    check_links(path, text, failures)


def main() -> int:
    if not PACKAGES_DIR.is_dir():
        print(f"error: {PACKAGES_DIR} does not exist", file=sys.stderr)
        return 1

    failures: list[str] = []
    counts = {"skill": 0, "agent": 0, "instruction": 0}

    for pattern, kind, required in PRIMITIVE_CONTRACTS:
        for path in sorted(PACKAGES_DIR.glob(f"*/{pattern}")):
            counts[kind] += 1
            check_primitive(path, kind, required, failures)

    check_discovery(failures)

    total = sum(counts.values())
    if total == 0:
        failures.append(f"{PACKAGES_DIR}: matched no primitives at all")
    if failures:
        for failure in failures:
            print(f"[x] {failure}")
        print(f"\n[x] {len(failures)} problem(s) across {total} primitives")
        return 1

    print(
        f"[+] {total} primitives valid "
        f"({counts['skill']} skills, {counts['agent']} agents, {counts['instruction']} instructions)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
