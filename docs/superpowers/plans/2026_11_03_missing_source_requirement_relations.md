# Missing source requirement relations implementation plan

> For agentic workers: use superpowers:executing-plans to implement this plan.
> Steps use checkbox syntax for tracking.

**Goal:** Export projects with unresolved source-marker UIDs in relaxed mode.

**Architecture:** Keep unresolved references in the file traceability index.
Expose them through the traceability index for the project warning ribbon.
Render missing requirements with a local source-view template.

**Tech stack:** Python 3.10+, Jinja, pytest, LIT/FileCheck, Invoke.

**Spec:**
[Design](../specs/2026-11-03-missing-source-requirement-relations-design.md)

## Global constraints

- Reuse `allow_missing_relation_requirements` and its existing CLI option.
- Keep strict-mode failures and existing query signatures.
- Missing references create no nodes, edges, or code coverage.
- Retain markers, valid links, roles, and skip-marker behavior.
- Count a range reference once, without counting its end marker again.
- Keep warning markup local; use the existing warning styles.
- Follow AGENTS.md and the SDG. Preserve the user's L2 requirements edits.

## Review focus

- Missing UIDs in C/C++ declarations must survive definition propagation.
- Mixed markers must retain valid links and count coverage only through them.
- Repeated references at distinct locations must retain their locations.
- Warning text must escape source UIDs before rendering HTML.
- Generated source nodes must never link to a missing requirement node.

## Task 1: Index and render unresolved source references

**Files:**

- Modify `strictdoc/core/file_traceability_index.py` for reference records,
  resolution guards, source-node links, and coverage filtering.
- Modify `strictdoc/core/traceability_index.py` for the query facade.
- Modify `strictdoc/core/traceability_index_builder.py` for source-page
  dependencies when no requirement resolves.
- Modify the source-view `view_object.py` for safe rendering.
- Create `missing_requirement.jinja` in the source-view template directory.
- Modify the shared `missing_relations_project_warning.jinja.html` template.
- Extend `tests/unit/strictdoc/core/test_file_traceability_index.py`.
- Create integration fixtures below
  `source_code_traceability/_validation/04_missing_requirements_relaxed/`.
- Update the user guide and Unreleased release notes.

**Interfaces:**

- Add `MissingSourceRequirementRelation`, a record containing
  `source_file: SourceFile`, `marker: RelationMarkerType`, and
  `requirement_uid: str`.
- Add `FileTraceabilityIndex.get_missing_requirement_relations(self,
  source_file_rel_path: Optional[str] = None)
  -> List[MissingSourceRequirementRelation]`.
- Add `TraceabilityIndex.get_missing_source_requirement_relations` with the
  same parameters and return type.
- These queries return lists without exposing mutable index storage.

- [x] Write unit tests using real parsed source markers and a real document
  index. Assert one missing reference for a begin/end pair, correct path and
  role, no missing-node graph links, and zero coverage for missing-only ranges.
  Assert coverage and links remain for a mixed valid/missing marker.
  Assert separate locations remain separate records and returned lists do not
  mutate index storage.
- [x] Run `invoke test-unit --focus missing_source_requirement`.
  Expected: the new relaxed-mode tests fail on the existing missing-UID error.
- [x] Add the reference record and queries. Record missing begin-marker UIDs
  and print source/location warnings in relaxed mode; retain strict errors.
  Guard missing lookups during source-node linking, declaration propagation,
  role validation, and coverage calculation.
- [x] Run the unit test command again. Expected: all tests pass.
- [x] Add integration fixtures with valid and missing references in range,
  line, function, class, and file scopes, plus C/C++ declarations and
  definitions. Exercise both CLI and configuration activation. Include skip
  markers, repeated references, mixed UIDs, and HTML-sensitive UID text.
- [x] Run `invoke test-integration --focus 04_missing_requirements_relaxed`.
  Expected: failure on unresolved source-view lookup or warning assertions.
- [x] Render missing UIDs through the local warning template in banner titles,
  details, and sidebars. Include unresolved source references in the project
  warning total. Keep valid rendering unchanged.
- [x] Run the focused integration command again. Expected: all assertions pass,
  including escaped warning text, valid links, warning counts, and coverage.
- [x] Add user documentation and an Unreleased note for the supported behavior.
- [x] Run `invoke test-unit`,
  `invoke test-integration --focus source_code_traceability`, and `invoke lint`.
  Expected: no regressions or lint failures caused by this change. Record any
  environment or baseline failures by name.
- [x] Commit the feature and tests together using a Conventional Commit.

## Execution and review

Implement inline in the isolated worktree. Keep a progress ledger with test
results and any decisions that adjust this plan. Obtain one fresh code review
against the SDG and approved design. Fix substantive findings with regression
tests before bringing the completed change back to the original feature branch.
