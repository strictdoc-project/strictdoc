---
name: sdoc-conventions
description: |
  Internal mechanics layer used by feature-docs and release-notes for any
  edit to a .sdoc file (docs/*.sdoc, including
  docs/strictdoc_04_release_notes.sdoc). Covers line width, MID handling,
  and the post-edit regeneration step — not prose style, see doc-voice for
  that.
---

# sdoc-conventions

Mechanical rules for editing any `.sdoc` file, shared by every skill that
does so. Source of truth is the SDG
(`docs/strictdoc_11_developer_guide.sdoc`, "Documentation" and other
sections) — re-read it if these rules seem stale, don't improvise past it.

## Line width

Every line is at most 80 characters. Wrap prose manually; StrictDoc's own
docs currently have a few pre-existing exceptions, but new content must
follow the 80-character limit regardless of what surrounds it.

## MID handling

Do not hand-author `MID` values. StrictDoc generates them. When adding a new
`[SECTION]` or `[TEXT]` node, leave `MID` absent (or as the tooling expects)
rather than inventing an ID.

## Match existing structure before writing

Before editing, read 2-3 neighboring sections in the target file. Match:

- The existing `SECTION`/`TEXT` grammar nesting.
- Terminology already established for the feature area — don't introduce a
  second name for something the doc already calls something else.

## After writing

Validate parsing:

    strictdoc export . --formats=html --output-dir /tmp/strictdoc_check

A non-zero exit or parser error means the edit broke structure or grammar;
fix before presenting the result. Delete the throwaway directory afterward.
