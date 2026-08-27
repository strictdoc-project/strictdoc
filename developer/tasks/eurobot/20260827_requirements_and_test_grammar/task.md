# System requirement and test grammar with rule traceability

## WHAT

Define a custom SDoc grammar for the Eurobot project with three elements:

- `RULE`: one node per numbered clause of the Eurobot competition rules,
  holding a UID (e.g. `RULE-3.2.1`) and the clause text.
- `REQUIREMENT`: a system (black box) requirement, with a `RELATIONS` field
  of type `Parent` pointing at the `RULE` node(s) it covers.
- `TEST_CASE`: a system test, with a `RELATIONS` field of type `Parent`
  pointing at the `REQUIREMENT` node(s) it verifies, and a `STATUS` field of
  type `SingleChoice(Not Executed, Blocked, Failed, Passed)` recording the
  current manual execution result.

The grammar shall let a reviewer answer three questions from the
Traceability Matrix and Deep Traceability screens without extra tooling:
which rules have no covering requirement, which requirements have no
covering test, and which tests are not yet passed. The `TEST_CASE` element
shall expose its `STATUS` value in the table view (`TABLE_SCREEN`) so a
mentor can scan test state without opening each node.

## WHY

The team asked whether StrictDoc can cover the Eurobot rules with system
requirements, and those requirements with system tests, with automatic
coverage checking. It can: `RELATIONS` plus the Traceability Matrix and Deep
Traceability screens already do this, and `SingleChoice` fields already
support the kind of manually maintained status value a test result needs. No
StrictDoc code changes are required, only a project-specific grammar.

This task is the backbone the rest of the Eurobot task set builds on: rules
import (needs `RULE` to exist), release versioning (adds a field to
`REQUIREMENT`), and the results dashboard (reads `STATUS` off `TEST_CASE`)
all depend on this grammar being in place first.

## HOW

Grammar location: declared in the Eurobot project's own `strictdoc_config.py`
(a separate project from this repository), not in this fork's own `docs/`.

Element design:

- `RULE` fields: `UID` (required, format `RULE-<section>.<clause>`),
  `TITLE`, `STATEMENT` (the clause text, verbatim from the rules).
- `REQUIREMENT` fields: the standard `UID`/`TITLE`/`STATEMENT`, plus
  `RELATIONS` with a `Parent` entry typed to `RULE`.
- `TEST_CASE` fields: `UID`/`TITLE`/`STATEMENT` (test procedure),
  `RELATIONS` with a `Parent` entry typed to `REQUIREMENT`, and `STATUS` as
  `SingleChoice(Not Executed, Blocked, Failed, Passed)`. The default value
  on creation should be `Not Executed`.

Relation type: use `Parent`, the same relation StrictDoc's own requirements
documents use for upward traceability, rather than inventing a custom
relation name. It is what the Traceability Matrix and Deep Traceability
screens already render without extra configuration.

Screens to enable in the Eurobot project's `project_features`:
`TRACEABILITY_MATRIX_SCREEN`, `DEEP_TRACEABILITY_SCREEN`, `TABLE_SCREEN` (for
the status-at-a-glance table view). `PROJECT_STATISTICS_SCREEN` is optional;
task `20260827_test_dashboard` supersedes it for status counts.

Forward compatibility: leave the `REQUIREMENT` element's field list easy to
extend. Task `20260827_release_versioning` adds a `TARGET_REVISION` field to
this same element; this task should not hardcode assumptions that would make
that addition awkward (for example, treating `RELATIONS` as the element's
last field).

### Deferred work

Grammar-level validation (for example, rejecting a `TEST_CASE` with no
`Parent` relation) is not covered by this task. StrictDoc's required/
optional field validation can enforce some of this later if gaps become a
recurring problem in practice.
