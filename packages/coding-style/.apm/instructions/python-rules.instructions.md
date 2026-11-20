---
description: Python style rules for agent-written code — keyword-only parameters, the project's identifier aliases, NamedTuple and enums for domain values, named exceptions, prompt text, async I/O, top-of-file imports, no unused export surfaces, and running the type checker.
applyTo: "**/*.py"
---

# Python Rules

These add to the Software Engineering Rules. Where a project's own convention differs, follow the project.

## Signatures

**Every function with more than one parameter starts with `*` (or `self, *`).** Before handing off, check each `def` you added or changed. A one-parameter function may end with `/`. Never write `/, *` in the middle of a list, and never insert a positional parameter into an existing signature.

```python
# bad
def drop_walk(engine, attempt_id, /, *, walk_id): ...

# good
def drop_walk(*, engine, attempt_id, walk_id): ...
```

A positional parameter inserted into an existing signature silently shifts every later argument at each call site that was not updated. Keyword-only parameters turn that into a loud error.

**A new parameter that every caller must decide gets no default.** A default that a caller can silently omit, especially on a safety flag, hides the caller you forgot to update.

## Types

**Use the project's identifier and domain aliases.** Before typing an id, path, slug or digest as `str`, `int` or `UUID`, search the project for an existing `NewType` or alias (often in a shared types module) and use it in every new signature, field and return type. Only define a new `NewType` when none exists. Convert once, where the value is created; never wrap a value that already has the type (`RequestId(request_id)`, `str(path)`) or widen it back to the primitive.

**No anonymous tuples for structured data.** A function returning more than one value, a multi-field dict or set key, and two lists paired by position all become a `NamedTuple` (or two distinct `NewType`s). Never read a tuple by index, and never explain tuple slots in a docstring.

**No `Any`, `object` or untyped `dict` in a signature.** Give a payload a small typed model, a callable a `Callable[...]` or `Protocol`, and a closed set of values the project's existing enum (or a new one). Never repeat enum values as string literals.

**Tagged unions get a discriminator, and code over them uses an exhaustive `match`** ending in `assert_never`. No catch-all `case _` and no `isinstance` chain with a default branch.

**Pass `strict=True` to `zip`** in production code. A length mismatch should fail, not drop items.

**Dataclasses hold data.** A type that is mostly behavior is a plain class with an explicit `__init__`.

**Fix the type instead of ignoring it.** When an ignore is unavoidable, scope it to the error code (`# type: ignore[attr-defined]`) and use only suppressions the project's lint config allows.

**Before the first commit, run the project's lint and type checker on the files you changed**, as configured in its pre-commit or CI config. Read that config first; do not assume no checker applies.

## Errors

**Raise the project's named exceptions, not built-ins.** When the project has an exceptions module or a domain error base, raise a named subclass of it for a domain failure, not `ValueError`, `RuntimeError`, `TypeError`, a bare `Exception` subclass, or a framework base such as `BadRequestException`. Add a new named class when none fits, and do not subclass an unrelated built-in to borrow its handling. Re-raise with `raise ... from err`.

**Keep exception messages constant.** Put identifiers, paths and counts in structured fields or logs, not in the message string, so error grouping stays stable.

**No `assert` outside tests.** `python -O` strips it. Narrow an `Optional` with an `if` that raises a named exception, or fix the type so the check is unnecessary.

## Async

**Do not block the event loop.** Inside `async def`, do not call synchronous file, network, S3, Redis or database I/O, or CPU-heavy work such as image decoding or large encodes. Use the async client, or move the call to a worker thread with the project's helper (for example `asyncio.to_thread`).

**Do not hold a database session across slow external work.** Close or commit the session before awaiting an HTTP call, renderer, upload or other external service, and open a new one afterwards.

## Prompt text

**Do not split prompt sentences across implicitly concatenated literals.** Write text the model reads (prompts, tool descriptions, examples) as a triple-quoted string passed through `textwrap.dedent` or `inspect.cleandoc`, or as a module-level constant, so the line breaks the model receives are the ones in the source. Do not wrap a sentence across adjacent string literals for line width, and do not build a stable tool description by conditional concatenation.

## Modules

**Imports go at the top of the file.** An import inside a function needs a real import cycle or a measured cost behind it, stated where it sits.

**No export surface without a consumer.** Do not declare `__all__` in a module nothing star-imports. Do not re-export names from a package `__init__` unless something imports them from the package root.

**A name imported from another module is public.** When you move or share a `_private` helper, drop the underscore. Do not import underscore names across modules.

**No local aliases for classes.** Write `IdentityRow.column`, not `stored = IdentityRow` followed by `stored.column`. A name bound with an ORM aliasing call is a real SQL alias and is fine.
