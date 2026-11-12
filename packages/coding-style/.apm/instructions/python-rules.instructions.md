---
description: Python style rules for agent-written code — keyword-only parameters, NewType and NamedTuple for domain values, top-of-file imports, no unused export surfaces, and running the type checker.
applyTo: "**/*.py"
---

# Python Rules

These add to the Software Engineering Rules. Where a project's own convention differs, follow the project.

## Signatures

**Never write `/, *` in the middle of a parameter list.** A function with one parameter may end with `/`. A function with more than one parameter starts with `*`, or with `self, *` on a method, so every argument is passed by name.

```python
# bad
def drop_walk(engine, attempt_id, /, *, walk_id): ...

# good
def drop_walk(*, engine, attempt_id, walk_id): ...
```

A positional parameter inserted into an existing signature silently shifts every later argument at each call site that was not updated. Keyword-only parameters turn that into a loud error.

## Types

**Give domain primitives a `NewType`.** A document path, a slug, a digest, or an identifier that travels through several functions gets a `NewType`, defined in the project's shared primitive-types module when it has one. Convert at the boundary where the value is created, not at each use.

**Return a `NamedTuple`, not a bare tuple, when a function returns more than one value.** Two `NewType`s of different kinds also work. The caller must not be able to unpack the values the wrong way round without a type error.

**Dataclasses hold data.** A type that is mostly behavior is a plain class with an explicit `__init__`.

**Run the project's type checker on the files you changed**, even when CI does not. A `NewType` mismatch passes lint and fails only under the checker.

## Modules

**Imports go at the top of the file.** An import inside a function needs a real import cycle or a measured cost behind it, stated where it sits.

**No export surface without a consumer.** Do not declare `__all__` in a module nothing star-imports. Do not re-export names from a package `__init__` unless something imports them from the package root.

**No local aliases for classes.** Write `IdentityRow.column`, not `stored = IdentityRow` followed by `stored.column`. A name bound with an ORM aliasing call is a real SQL alias and is fine.
