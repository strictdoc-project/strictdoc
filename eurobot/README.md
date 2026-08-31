# Eurobot reference project

A runnable StrictDoc project holding the Eurobot course's document grammar:
`RULE`, `REQUIREMENT`, and `TEST_CASE` elements linked by `Parent` relations.
This project implements
`developer/tasks/eurobot/20260827_requirements_and_test_grammar`,
`developer/tasks/eurobot/20260827_eurobot_rules_import`, and
`developer/tasks/eurobot/20260827_release_versioning`.

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
screens the course relies on. `Eurobot_Requirements.sdoc` and
`Eurobot_Tests.sdoc` hold the seed content. `Eurobot_Rules.sdoc` is generated
by `tools/import_rules.py` from the Russian rules PDFs under
`_assets/rules/source/`: the PRO rules, which cover entry and the robots, and
the 2026 game rules.

The rules are in Russian and the requirements and test cases are in English,
because the rules are quoted from the competition documents while the
requirements are the course's own writing.

## Importing the rules

```bash
python eurobot/tools/import_rules.py --project-dir eurobot
```

The converter reads every PDF named in
`_assets/rules/source/sources.json`, splits it into numbered clauses, and
merges those clauses into `Eurobot_Rules.sdoc`. It writes the images it finds
to `_assets/rules/<source prefix>/` and references them from the clause they
appear under.

Run it again on the same PDFs and it writes nothing: the document stays
byte-identical, so a re-import leaves no diff for anyone to review.

### Two source layouts

A PDF says how it carries its headings through the `layout` field in
`sources.json`.

`headings-in-text` suits a PDF built by LaTeX, where a heading is a line of
text like any other. The converter recognises it on its way down the page.

`headings-in-toc` suits a Google Docs export, which is what the current Russian
sources are. That renderer turns every chapter and section heading into a
picture, leaving only the third level (`F.4.a.`) as text, so the words
`РАЗМЕРЫ` and `БЕЗОПАСНОСТЬ` appear on the contents page and nowhere else in
the file. The converter reads the structure from the table of contents instead:
the contents page names each clause and gives its printed page, and the picture
on that page marks where the clause starts. Nothing reads the pixels, so no
optical character recognition is involved. Where the count of contents entries
and pictures on a page disagrees, the clause is anchored at the top of the page
and its boundary is coarse rather than lost.

### What happens when the rules change

Drop the new PDF in over the old one, keeping the file name, and run the
converter again. It reconciles by UID instead of regenerating the document:

- A clause that is in both keeps its node and takes the new text. The change
  shows up as one line in `git diff`, because each paragraph is one line.
- A clause that only the new PDF has becomes a new node with
  `STATUS: Active`.
- A clause that has disappeared keeps its node, keeps its last known text,
  and gets `STATUS: Removed`.

The converter never deletes a node. A `REQUIREMENT` whose `Parent` points at
a UID that no longer exists is not a warning in StrictDoc:
`traceability_index_builder.py` raises `StrictDocException` and aborts the
whole export or server rebuild, for every student, over one dropped rule.

After an import that reports removed clauses, find the requirements that are
now covering nothing. Search `node["STATUS"] == "Removed"` on the search
screen to list the removed rules, then read their `Parent [COVERS]` column on
the Traceability Matrix to see which requirements point at them. A mentor
decides, per requirement, whether to cancel it or delete it. The converter
does not make that call.

One warning deserves care. A translation is not a revision: the Russian rules
renumber parts of the English ones, so `I.2` means one clause in the Russian
PRO document and another in the English general rules. Swapping the language of
a source is a job for regenerating the document from scratch, not for the merge
above.

### UIDs

A rule's UID is `RULE-<source prefix>-<clause number>`, for example
`RULE-GENERAL-F.4.c` or `RULE-2026-E.1.b`. The prefix comes from
`sources.json` and keeps the two rules documents apart: both number their
chapters from A, so `D.1.` means one thing in the PRO rules and another
in the 2026 game rules.

The 2026 season's prefix is the season year on purpose. Next season's rules
reuse the same chapter letters for different content, so a year prefix makes
those new clauses new nodes rather than silent rewrites of the old ones.

### What the extraction does not get right

- Three clauses carry no extracted text: `I.2`, `J.1` and `J.2` of the PRO
  rules. Their statement says so and points at the source page. `J.1` and
  `J.2` are tables of materials and tolerances. `I.2` is a quirk of the
  source, which numbers that clause `I.2` in the contents and its
  sub-headings `I.3.a` through `I.3.c` in the body.
- A paragraph the source rasterised appears in the statement as an image
  rather than as searchable text. The PRO rules hold about a dozen.
- Every chapter and section title comes from the table of contents verbatim,
  including its typos: `I.1` reads `ОСНОВАНЯ ИНФОРМАЦИЯ` in the source.
- A drawing arrives as one large picture surrounded by dozens of small ones
  holding its dimension callouts. The converter keeps images above a minimum
  size and drops the callouts, so a technical drawing is readable but not
  annotated.

The source PDFs stay in `_assets/rules/source/` and are copied to the HTML
output, so a reader who doubts a clause can open the original.

## What the screens answer

Which rules have no covering requirement? Read the Traceability Matrix's
`Parent [COVERS]` column. Most of the 93 imported rules are empty there,
including `RULE-GENERAL-F.4.b`, the clause on energy sources
(`ИСТОЧНИКИ ЭНЕРГИИ`). Closing that gap is the course's own work.

Which requirements have no covering test? Read the same screen's
`Parent [VERIFIES]` column. `REQ-4` is empty there, and Deep Traceability
shows the same gap as a chain that stops at the requirement.

Which tests are not yet passed? Read the Table screen's `STATUS` column.
`TC-2` is `Not Executed` and `TC-3` is `Failed`.

## Planning a requirement for a revision

`REQUIREMENT` carries `TARGET_REVISION`, the identifier of the revision
(`C1`, `C2`, ...) a requirement is planned or implemented for, one of the
course's own revision names (`major.minor`, for example `C1` for the first
minor of the major revision codenamed Cortana). `REQ-1` and `REQ-2` are
planned for `C1`, `REQ-3` for `C2`, and `REQ-4` is `TBD`: nobody has
scheduled it yet.

Growing the choice list, when a new minor starts, is a hand-edit of
`eurobot_grammar.sgra`'s `TARGET_REVISION: SingleChoice(...)` line, the same
way `RULE`'s `STATUS` choices were declared. The document grammar editor in
StrictDoc's web UI cannot do this: its "edit element" screen has no field
for a `SingleChoice`'s options, and saving through it rewrites every field
of the element, `TARGET_REVISION` included, as a plain `String`, discarding
whatever choices it had. Edit the `.sgra` file directly instead.

To find the tests to run for a revision, run a Query Engine search and read
its result off the Traceability Matrix:

- One revision: `node["TARGET_REVISION"] == "C1"` lists the requirements due
  by `C1`.
- Several revisions, for cumulative planning:
  `(node["TARGET_REVISION"] == "C1" or node["TARGET_REVISION"] == "C2")`.
  `any(["C1", "C2"]) in node["TARGET_REVISION"]` reads shorter but checks
  substring containment, not exact equality, on every field except `TAGS`:
  once minors reach two digits, `any(["C1"]) in ...` would also match a
  requirement targeted at `C10`. The `==`/`or` chain has no such risk.

Cross-reference the matching requirement UIDs against the Traceability
Matrix's `Parent [VERIFIES]` column to read off their `TEST_CASE` nodes:
that list is the revision's test plan.

Recovering a past RC's results is a `git` question, not a `TARGET_REVISION`
question: `STATUS` holds one current value per `TEST_CASE`, not a history.
Enable `"DIFF"` in `project_features` and run
`strictdoc export . --generate-diff-git "C1_RC1..C1_RC2"`, or open
`/diff?left_revision=C1_RC1&right_revision=C1_RC2` on a running
`strictdoc server`, to see which `TEST_CASE` statuses and which
`REQUIREMENT` nodes changed between two tags. Cutting those weekly RC tags,
and keeping the letter-to-codename glossary, is the downstream Eurobot
project's own convention: this reference project does not carry git tags of
its own to demonstrate it against.

## Conventions the grammar does not enforce

`RULE` UIDs follow the pattern above. `UID` is a plain `String` field, and
StrictDoc does not check the pattern.

A new `TEST_CASE` starts at `STATUS: Not Executed`, and an imported `RULE`
at `STATUS: Active`. Grammar fields have no default value, so both `STATUS`
fields, and `TARGET_REVISION`, are declared `REQUIRED: True`: a node
without a value fails validation instead of silently carrying none at all.

Any `SingleChoice` field, `TARGET_REVISION` included, always accepts `TBD`
and `TBC` on top of its declared choices: StrictDoc treats both as
placeholder values regardless of the choice list. `REQ-4` uses
`TARGET_REVISION: TBD` for exactly that reason: nobody has scheduled it for
`C1` or `C2` yet, and `TBD` says so without inventing a revision to hold it.

Relation roles say what a relation means, because relation types cannot. A
grammar relation is `TYPE: Parent` plus an optional `ROLE`, and it cannot be
typed to a target element. `REQUIREMENT` uses `ROLE: COVERS` and `TEST_CASE`
uses `ROLE: VERIFIES`, which the Traceability Matrix renders as separate
columns.

## Field order

Every field before the content field (`STATEMENT`) is single-line meta
information, and each node's field order must match the grammar's. So a new
single-line field goes between `TITLE` and `STATEMENT`. That is where `RULE`
carries `STATUS` and `REQUIREMENT` carries `TARGET_REVISION`.

## Seed content

`Eurobot_Rules.sdoc` holds the real clauses of the two rules documents. Do
not edit it by hand: the next import overwrites every statement.

The four requirements and three test cases are seed content. They cover
three of the 93 rules and show the shape the course writes, not the course's
actual requirement set.
