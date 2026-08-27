# Import the Eurobot Rules into a linked reference document

## WHAT

A deterministic converter that turns the Eurobot Rules PDF documents into a
`Eurobot_Rules.sdoc` document made of `RULE` nodes (defined in
`20260827_requirements_and_test_grammar`), one node per numbered rule
clause, each with a stable UID that a `REQUIREMENT` can trace to. The
original PDFs stay attached to the project as reference assets, so a reader
can check a `RULE` node against the source text it came from.

The converter shall be safe to run again on the same PDF and produce no
change, and safe to run again on a revised PDF without breaking any
existing `REQUIREMENT`'s trace to a `RULE`:

- Running it twice on an unchanged PDF shall leave `Eurobot_Rules.sdoc`
  byte-identical: no new git diff, no reordered nodes, no incidental
  reformatting.
- Running it on a revised PDF shall update the text of a rule that changed,
  add a node for a rule that is new, and never delete a node for a rule that
  disappeared. A disappeared rule shall instead get `STATUS: Removed` added
  to its `RULE` node, defined by this task as `SingleChoice(Active,
  Removed)`.
- The task shall also produce, as a required step after each re-import, a
  Query Engine query listing `REQUIREMENT` nodes whose only `RULE` links now
  have `STATUS: Removed`, for a human to decide whether to mark that
  requirement cancelled or delete it.
- Embedded images (diagrams, field layouts) shall carry over into the
  `RULE` node's `STATEMENT` as an RST or Markdown image reference pointing
  at an extracted asset file, not be dropped.

## WHY

The team rejected the original approach in this task (manually transcribing
extracted PDF text by hand) as error-prone: typos, skipped clauses, and
inconsistent chunking are exactly the kind of mistake a person retyping
dozens of numbered clauses will make. Reviewing the actual codebase points
to a converter instead of a manual step, and shapes what that converter has
to do:

- StrictDoc has no PDF backend today. Its `strictdoc/backend/*` formats
  cover sdoc, markdown, RST, ReqIF, Excel, SPDX, Gcov, JSON, and source code
  only, so a PDF's content has to be extracted before it can become
  traceable nodes.
- `pypdf`, already a StrictDoc dependency, is capable of doing that
  extraction (`page.extract_text()` for text, `page.images` for embedded
  images) even though nothing in the codebase uses it for reading an input
  PDF today; its only current use is post-processing StrictDoc's own
  generated PDFs in `strictdoc/features/html2pdf/`. No new dependency is
  needed.
- A PDF has no machine-readable structure the way ReqIF (a standardized XML
  schema) or Excel (a spreadsheet with known columns) does: headings are a
  visual convention, not tagged data. That is why StrictDoc's two real
  import-`Format` precedents, `ReqIFFormat` and `ExcelFormat`, both work
  against a fixed, machine-generated schema rather than parsing free-form
  documents generically. General-purpose PDF import is not a reliable
  target for the same reason; a converter scoped to this rules document's
  own numbering convention is.
- A `REQUIREMENT`'s `RELATIONS` field pointing at a `RULE` UID that no
  longer exists is not a soft warning in StrictDoc. Confirmed in
  `strictdoc/core/traceability_index_builder.py` (and the integration tests
  under `tests/integration/features/sdoc/graph_consistency/
  07_parent_requirement_does_not_exist/` and `tests/integration/features/
  html/child_relations/03_child_link_does_not_exist/`): a dangling relation
  raises `StrictDocException` and aborts the entire `export`/`server` run
  for the whole project, not just the affected document. That single fact
  rules out ever deleting a `RULE` node once it has existed, whether the
  rule was dropped from the competition or just renumbered: doing so would
  crash the shared server the next time anyone re-exports, for every
  student, over one rule change.

## HOW

Extraction: read each PDF page's text with `page.extract_text()` and split
it into clauses by matching the rules' own numbering pattern (for example
`\d+\.\d+(\.\d+)?`) against that text. Normalize whitespace and rejoin
PDF line wraps the same way on every run, so the same input always produces
the same extracted string.

Images: read each page's embedded images via `page.images`, save each to an
assets folder (for example `assets/rules/`), and name the file from the
owning rule's UID plus a stable index (not the PDF's internal object order),
so re-running on the same PDF produces the same file names. Insert the
matching `.. image::` (RST) or `![]()` (Markdown) reference into the
`STATEMENT` at the point the image occurred.

Merging into `Eurobot_Rules.sdoc`: read the existing document, if one
exists, and reconcile it against the newly extracted clauses by UID rather
than regenerating the file from nothing:

- A UID present in both keeps its node; update `STATEMENT` only if the
  extracted text actually changed. A real change becomes a normal,
  reviewable line in `git diff` on the committed file, which is enough to
  flag it for the team without extra tooling.
- A UID only in the new extraction becomes a new `RULE` node with
  `STATUS: Active`.
- A UID only in the previous file, missing from the new extraction, keeps
  its node and gets `STATUS: Removed`. Its `STATEMENT` stays as the last
  known text.
- On the very first run, with no prior file, every extracted clause is a
  new `RULE` node with `STATUS: Active`.

No-op detection: before writing, compare the merged result against the
existing file's content and skip the write entirely if nothing changed,
matching how StrictDoc's own move-node feature avoids touching
`last_updated` on a no-op move.

Review query after each re-import: run, in the Query Engine search screen,
a query for `REQUIREMENT` nodes whose only `Parent` targets have `STATUS:
Removed` (a two-step check today: filter `RULE` nodes by `STATUS`, then
cross-reference the `REQUIREMENT`s that trace to them in the Traceability
Matrix, since the Query Engine does not traverse into a relation's target
fields directly). Hand that list to a mentor to decide, per requirement,
whether to mark it cancelled or delete it once nothing else, such as a
`TEST_CASE`, still traces to it. This step stays a human decision rather
than something the converter automates, for the same crash-on-delete reason
above.

Keep the two source PDFs in the project (for example under
`assets/rules/source/`) and reference them from the document's
introduction, so a reviewer can check a `RULE` node's text against the
original.

### Deferred work

- Renumbering, the same rule content reappearing under a different clause
  number, is not detected automatically. It looks identical to one rule
  disappearing and an unrelated one appearing, and stays a manual check
  during review.
- Promoting this converter into a registered `Format`
  (`strictdoc/core/format.py`, wired into `strictdoc convert`) is worth
  doing once the team re-imports a rules revision often enough to justify
  it. Until then, it runs as a standalone script.
- `20260827_requirements_and_test_grammar` should leave room for a
  lifecycle field on `REQUIREMENT` (for example
  `SingleChoice(Draft, Active, Cancelled)`) to receive the "mark cancelled"
  decision from the review query above; this task defines `RULE`'s
  `STATUS` field but not that one.
