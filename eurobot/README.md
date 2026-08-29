# Eurobot reference project

A runnable StrictDoc project holding the Eurobot course's document grammar:
`RULE`, `REQUIREMENT`, and `TEST_CASE` elements linked by `Parent` relations.
This project implements
`developer/tasks/eurobot/20260827_requirements_and_test_grammar`.

It lives inside this fork so that the grammar can be exported and regression
tested here. Nothing in it reaches outside this folder, so the course's own
Eurobot repository can take a copy of the folder as its starting point.

## Running it

```bash
strictdoc export eurobot --output-dir build/eurobot_html
strictdoc server eurobot
```

Both commands read `eurobot/strictdoc_config.py`, which StrictDoc picks up
from the input directory.

## Files

`eurobot_grammar.sgra` holds the grammar, shared by all three documents.
`strictdoc_config.py` registers it under the alias `@eurobot` and enables the
screens the course relies on. `Eurobot_Rules.sdoc`,
`Eurobot_Requirements.sdoc`, and `Eurobot_Tests.sdoc` hold the seed content.

## What the screens answer

The seed documents leave one instance of each coverage gap visible, so the
screens show real answers instead of empty tables.

Which rules have no covering requirement? Read the Traceability Matrix's
`Parent [COVERS]` column. `RULE-7.1` is empty there.

Which requirements have no covering test? Read the same screen's
`Parent [VERIFIES]` column. `REQ-4` is empty there, and Deep Traceability
shows the same gap as a chain that stops at the requirement.

Which tests are not yet passed? Read the Table screen's `STATUS` column.
`TC-2` is `Not Executed` and `TC-3` is `Failed`.

## Conventions the grammar does not enforce

`RULE` UIDs follow `RULE-<section>.<clause>`, matching the clause numbering of
the competition rules. `UID` is a plain `String` field, and StrictDoc does not
check the pattern.

A new `TEST_CASE` starts at `STATUS: Not Executed`. Grammar fields have no
default value, so `STATUS` is declared `REQUIRED: True` instead: a test case
without a status fails validation instead of silently carrying no status at
all.

Relation roles say what a relation means, because relation types cannot. A
grammar relation is `TYPE: Parent` plus an optional `ROLE`, and it cannot be
typed to a target element. `REQUIREMENT` uses `ROLE: COVERS` and `TEST_CASE`
uses `ROLE: VERIFIES`, which the Traceability Matrix renders as separate
columns.

## Field order

Every field before the content field (`STATEMENT`) is single-line meta
information, and each node's field order must match the grammar's. So a new
single-line field goes between `TITLE` and `STATEMENT`. That is where
`developer/tasks/eurobot/20260827_release_versioning` adds `TARGET_REVISION`
to `REQUIREMENT`, and where `20260827_eurobot_rules_import` adds `STATUS` to
`RULE`.

## Seed content

The `RULE` nodes paraphrase clauses of the Eurobot competition rules. None of
them is the verbatim rule text. The converter from
`developer/tasks/eurobot/20260827_eurobot_rules_import` replaces
`Eurobot_Rules.sdoc` with clauses extracted from the official PDF. The
requirements and test cases show the shape the course writes, not the course's
actual requirement set.
