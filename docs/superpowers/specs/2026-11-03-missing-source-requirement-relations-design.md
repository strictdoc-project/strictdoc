# Missing requirement references in source files

Status: approved on 2026-11-03.

## Goal

Extend relaxed relation handling to source markers that reference missing
requirement UIDs. Use the existing `allow_missing_relation_requirements`
configuration and `--allow-missing-relation-requirements` option.

## Approaches

The proposed approach retains source markers and displays unresolved UIDs as
warnings. It matches the existing handling of other missing relations.

An alternative logs warnings and removes unresolved references from the source
view. That needs fewer rendering changes, but hides the broken references.

## Behavior

- Strict mode continues to reject references to missing requirements.
- Relaxed mode reports each missing UID with its source path and location.
- Source banners and sidebars display missing UIDs as warnings without links
  to nonexistent requirements. Valid UIDs in the same marker remain linked.
- Missing references create no requirement nodes or graph edges. They contribute
  no code coverage; a mixed marker contributes coverage through its valid UIDs.
- A range reference counts once, without counting its matching end marker again.
- Line, range, function, class, and file markers follow the same rules. Existing
  skip markers retain their behavior.

## Implementation scope

Store unresolved references in the file traceability index with their UID, path,
marker location, and role. Add read-only queries for rendering and warning
counts.
Keep existing query signatures and return types.

Guard resolution during indexing, coverage calculation, and C/C++ declaration
propagation. Render missing references through source-view templates and
existing warning styles.

The shared changes requiring approval are the traceability index queries and the
project warning ribbon, whose total will include unresolved source references.
Keep the new source warning markup local to the source-view feature.

Document the behavior and add an Unreleased release note.

## Validation

Retain the existing strict-mode integration test. Add relaxed-mode integration
tests for configuration and CLI activation, mixed valid and missing UIDs, marker
scopes, escaped warning text, source-page generation, and coverage counts.

Add focused unit tests for unresolved-reference queries and paired-marker
counts.
Check C/C++ declaration propagation and valid source links for regressions.
Run the relevant Invoke tests and lint checks.
