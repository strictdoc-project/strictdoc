# Introduce Python API layer: `strictdoc.api`

## WHAT

Provide a dedicated `strictdoc.api` module that exposes the primary classes
that make up the public Python API.

Use `strictdoc/api/__init__.py`, not `strictdoc/api.py`.

## WHY

A dedicated API layer provides a stable import path for Python users.
Importing public objects exclusively from `strictdoc.api` allows the internal
implementation to be reorganized without breaking compatibility for users of
the StrictDoc Python API.

## HOW

- Expose the required public classes from `strictdoc.api`.
- Update all code outside the `strictdoc/` package to import these classes
  from `strictdoc.api` instead of their internal modules.

### Do include

- Primary domain classes: ProjectConfig, document models, TraceabilityIndex,
  all generators and view objects.
- `MID`
- `assert_cast`

### Do not include

- Test helpers
