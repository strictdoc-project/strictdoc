---
name: release-notes
description: |
  Use at the end of a task when the user asks to update the changelog or
  release notes, or when the user asks for a PR title and description.
  Writes release notes entries into docs/strictdoc_04_release_notes.sdoc
  following the existing SDG playbook, and drafts PR titles/descriptions
  using a fixed two-sentence result+mechanism+reason formula. Not for
  docs/*.sdoc feature documentation — see the feature-docs skill for that.
---

# Release notes and PR summaries

Two related but distinct outputs. Work out which one the user wants before
writing anything — they are not interchangeable, and a task's end can call
for either or both.

## Mode 1: release notes entry

Target file: `docs/strictdoc_04_release_notes.sdoc`.

The format is already specified in the SDG
(`docs/strictdoc_11_developer_guide.sdoc`, section "How to update release
notes"). Re-read that section before writing — it is the source of truth,
this skill only points at it. Do not improvise a different format even if
these notes are stale.

Reminders (not a substitute for the SDG section above):

- Write into the "Unreleased" top section; create it if it doesn't exist yet.
- The section body starts with `This release contains the following
  enhancements:` followed by a blank line, then numbered items (`1\)`, `2\)`,
  ...).
- A bug fix is a numbered item prefixed `Fixed: `, not a separate heading —
  match the existing entries' pattern.
- Summarize only `feat:` and `fix:` commits since the latest git tag. Ignore
  every other commit type and do not summarize commit-by-commit.
- Never touch previously released sections.
- Never touch `CHANGELOG.md`. It is a deprecated, auto-generated artifact;
  the SDG says to ignore it completely.
- Do not create a new version/section header yourself; that is a separate,
  not-yet-defined playbook.

To find the commits in scope:

```
git describe --tags --abbrev=0
git log <tag>..HEAD --oneline
```

## Mode 2: PR title and description

Triggered when the user asks for a PR title/description, typically once the
implementation is done.

Description formula, two sentences, no more:

1. Result, stated as a fact, action verb, past tense, no lead-up. What was
   done — not what the problem used to be.
2. The concrete mechanism (the actual event, function, or entity — not an
   abstraction like "changed the logic") plus the reason, one clause:
   "because X needed Y."

Forbidden in the description: "was/became" before/after framing, testing
details, bug or investigation history, any trailing "let me know if..."
closer.

Title: short, matches the style of recent merged PR titles on `main`
(`git log --oneline -20 main`) — this repo mixes imperative and
`area: change` noun-phrase titles depending on scope; follow whichever the
target files' recent history uses.

## Before returning either output

Run `doc-voice` on the drafted text and apply its findings before presenting
the result.
