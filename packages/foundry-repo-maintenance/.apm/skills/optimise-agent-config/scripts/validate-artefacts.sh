#!/usr/bin/env bash
# Validate APM artefact frontmatter for skills, agents and instructions.
#
# Usage: ./scripts/validate-artefacts.sh [repository-root]
#
# APM primitive contract:
#   skills       .apm/skills/<name>/SKILL.md               -> name, description
#   agents       .apm/agents/<name>.agent.md               -> description
#   instructions .apm/instructions/<name>.instructions.md  -> description, applyTo
#
# The same contracts are checked on the deployed copies under .agents/, .cursor/,
# .claude/ and .github/. An instruction's scope field is applyTo in APM sources
# and on GitHub Copilot, globs on Cursor and paths on Claude Code; any of the
# three satisfies the scope requirement. APM drops `description` when it deploys
# a rule to Claude Code, so a .claude/rules copy needs only a scope.
#
# Reports, per file, whether the required frontmatter fields are present and
# exits non-zero when any required field is missing. Run from the repository
# root, or pass the root as the first argument.

set -u

RED=$'\033[0;31m'
YELLOW=$'\033[0;33m'
BLUE=$'\033[0;34m'
GREEN=$'\033[0;32m'
NC=$'\033[0m'

root="${1:-.}"

errors=0
warnings=0

print_header() { printf '\n%s=== %s ===%s\n' "$BLUE" "$1" "$NC"; }
print_file()   { printf '\n  Checking %s...\n' "$1"; }
pass()         { printf '    %sOK%s\n' "$GREEN" "$NC"; }

error() {
    printf '    %sERROR:%s %s\n' "$RED" "$NC" "$1"
    errors=$((errors + 1))
}

warn() {
    printf '    %sWARNING:%s %s\n' "$YELLOW" "$NC" "$1"
    warnings=$((warnings + 1))
}

frontmatter() {
    awk '/^---[[:space:]]*$/ { if (++count == 2) exit } count == 1 { print }' "$1"
}

has_field() {
    printf '%s\n' "$1" | grep -q "^$2:"
}

field_value() {
    printf '%s\n' "$1" \
        | sed -n "s/^$2:[[:space:]]*//p" \
        | head -n 1 \
        | sed "s/[[:space:]]*$//; s/^['\"]//; s/['\"]$//"
}

has_frontmatter() {
    [ "$(sed -n '1p' "$1")" = "---" ]
}

# True when a scope key carries a value, whether inline (`globs: "**/*"`) or as a
# block sequence (`paths:` followed by indented items, which is the shape APM
# deploys to Claude Code).
has_scope_value() {
    printf '%s\n' "$1" | awk -v key="$2" '
        $0 ~ "^" key ":" {
            rest = substr($0, length(key) + 2)
            gsub(/[[:space:]]/, "", rest)
            if (rest == "[]") exit
            if (rest != "") { found = 1; exit }
            in_block = 1
            next
        }
        in_block {
            if ($0 ~ /^[[:space:]]+-[[:space:]]*[^[:space:]]/) { found = 1; exit }
            if ($0 !~ /^[[:space:]]/) exit
        }
        END { exit !found }
    '
}

validate_skill() {
    file="$1"
    expected_name=$(basename "$(dirname "$file")")
    print_file "$file"
    errors_before=$errors

    if ! has_frontmatter "$file"; then
        error "missing required frontmatter (no opening ---)"
        return 1
    fi

    fm=$(frontmatter "$file")

    if ! has_field "$fm" name; then
        error "missing required 'name' field"
    else
        name=$(field_value "$fm" name)
        if [ -z "$name" ]; then
            error "'name' field is empty"
        else
            [ "$name" != "$expected_name" ] && error "'name' ($name) does not match directory name ($expected_name)"
            printf '%s' "$name" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$' || warn "'name' should use lowercase letters, digits and single hyphens"
            [ "${#name}" -gt 64 ] && warn "'name' exceeds 64 characters"
        fi
    fi

    if ! has_field "$fm" description; then
        error "missing required 'description' field (agent cannot discover this skill)"
    else
        description=$(field_value "$fm" description)
        [ -z "$description" ] && error "'description' field is empty"
        [ "${#description}" -gt 1024 ] && warn "'description' exceeds 1024 characters"
    fi

    [ "$errors" -eq "$errors_before" ] && pass
    return 0
}

validate_agent() {
    file="$1"
    print_file "$file"
    errors_before=$errors

    if ! has_frontmatter "$file"; then
        error "missing required frontmatter (no opening ---)"
        return 1
    fi

    fm=$(frontmatter "$file")

    if ! has_field "$fm" description; then
        error "missing required 'description' field (host cannot auto-delegate)"
    else
        [ -z "$(field_value "$fm" description)" ] && error "'description' field is empty"
    fi

    [ "$errors" -eq "$errors_before" ] && pass
    return 0
}

validate_instruction() {
    file="$1"
    print_file "$file"
    errors_before=$errors

    if ! has_frontmatter "$file"; then
        error "missing required frontmatter (no opening ---)"
        return 1
    fi

    fm=$(frontmatter "$file")

    # APM drops `description` when it deploys a rule to Claude Code, so only the
    # source form and the hosts that keep the field are required to carry one.
    case "$file" in
        */.claude/rules/*) ;;
        *)
            if ! has_field "$fm" description; then
                error "missing required 'description' field"
            else
                [ -z "$(field_value "$fm" description)" ] && error "'description' field is empty"
            fi
            ;;
    esac

    scope_field=""
    for candidate in applyTo globs paths; do
        if has_field "$fm" "$candidate"; then
            scope_field="$candidate"
            break
        fi
    done

    if [ -z "$scope_field" ]; then
        error "missing required scope field (expected applyTo, globs or paths)"
    elif ! has_scope_value "$fm" "$scope_field"; then
        error "'$scope_field' field is empty"
    fi

    [ "$errors" -eq "$errors_before" ] && pass
    return 0
}

validate_collection() {
    kind="$1"
    shift
    found=0

    for directory in "$@"; do
        [ -d "$root/$directory" ] || continue

        case "$kind" in
            skill)
                for file in "$root/$directory"/*/SKILL.md; do
                    [ -f "$file" ] || continue
                    found=$((found + 1))
                    validate_skill "$file"
                done
                ;;
            agent)
                for file in "$root/$directory"/*.md; do
                    [ -f "$file" ] || continue
                    found=$((found + 1))
                    validate_agent "$file"
                done
                ;;
            instruction)
                for file in "$root/$directory"/*.md "$root/$directory"/*.mdc; do
                    [ -f "$file" ] || continue
                    found=$((found + 1))
                    validate_instruction "$file"
                done
                ;;
        esac
    done

    [ "$found" -eq 0 ] && printf '  No %ss found in the scanned directories\n' "$kind"
    return 0
}

printf 'APM Artefact Validator\n'
printf '======================\n'
printf 'Repository root: %s\n' "$root"

print_header "Skills (name, description)"
validate_collection skill .apm/skills .agents/skills .cursor/skills .claude/skills

print_header "Agents (description)"
validate_collection agent .apm/agents .cursor/agents .claude/agents .github/agents

print_header "Instructions (description, scope)"
validate_collection instruction .apm/instructions .cursor/rules .claude/rules .github/instructions

print_header "Summary"
printf '  Errors:   %s%s%s\n' "$RED" "$errors" "$NC"
printf '  Warnings: %s%s%s\n' "$YELLOW" "$warnings" "$NC"

if [ "$errors" -gt 0 ]; then
    exit 1
fi
