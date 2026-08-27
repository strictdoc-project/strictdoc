# Import the Eurobot Rules into a linked reference document

## WHAT

Turn the two Eurobot Rules PDF documents into a `Eurobot_Rules.sdoc`
document made of `RULE` nodes (defined in
`20260827_requirements_and_test_grammar`), one node per numbered rule
clause, each with a stable UID that a `REQUIREMENT` can trace to. The
original PDFs stay attached to the project as reference assets, so a reader
can check a `RULE` node against the source text it was transcribed from.

## WHY

StrictDoc has no PDF backend. Its `strictdoc/backend/*` formats cover sdoc,
markdown, RST, ReqIF, Excel, SPDX, Gcov, JSON, and source code only. There is
no way to import a PDF's structure automatically today, so the rules have to
become structured, linkable nodes by another route before requirements can
trace to them.

## HOW

Phase 1, in scope for this task:

1. Extract the rules text from both PDFs.
2. Split the text by rule number into individual clauses.
3. Write each clause as a `RULE` node in `Eurobot_Rules.sdoc`, with `UID`
   following the rule's own numbering (e.g. `RULE-3.2.1` for section 3,
   clause 2.1), so the UID stays meaningful to someone reading the original
   rules alongside it.
4. Keep the two source PDFs in the project (for example under an
   `assets/rules/` folder) and reference them from the document's
   introduction, so a reviewer can spot-check a transcription against the
   original.

This is a one-time job per rules revision (the Eurobot rules are typically
published once per season), done by hand or with a script over the extracted
text. It does not need to run automatically.

### Deferred work

A custom `Format` (`strictdoc/core/format.py`) that parses the rules PDF
directly on `convert` is worth building only if the rules PDF's structure
turns out consistent enough to parse reliably, and the team re-imports a new
revision often enough to justify it. Not undertaken here: Phase 1's manual
transcription should be enough for one season.
