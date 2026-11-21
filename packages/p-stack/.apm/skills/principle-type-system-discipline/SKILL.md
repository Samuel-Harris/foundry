---
name: principle-type-system-discipline
description: "Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, exhaust variants, derive from authoritative schemas."
disable-model-invocation: true
---

# Type System Discipline

Make the compiler reject impossible states, mismatched primitives, and unhandled variants.

- **One variant, one tag.** When fields only make sense together, or one field decides which others apply, model a tagged union with a literal tag. Never parallel optional fields, flags, sentinels or positional tuples that can disagree. Narrow by the tag, not by which field is present.
- **Exhaust every variant.** A `switch` or `match` over a union or enum handles every member and ends in a never or `assert_never` arm, so adding a member fails the build. A catch-all arm that returns a default hides the new member.
- **Brand semantic primitives.** If two arguments share a primitive type but mean different things, give each its own type. Validate once at creation.
- **External data is untyped until parsed.** JSON, RPC payloads, CLI args, config, environment variables, and database rows go through a parse function at the boundary that returns the typed model.
- **Derive types from authoritative schemas.** When a schema file owns a shape, derive the type from it instead of hand-rolling a parallel one.

For TypeScript syntax, see the **typescript-best-practices** skill.
