---
name: release-notes
description: |
  Use when the user asks to update the changelog or release notes. Also
  offer this proactively whenever the user asks for a PR title/description
  (see the commit-message skill) for a non-trivial change — that request is
  the reliable signal the work is considered done, which is otherwise not
  something this agent can infer on its own. Writes entries into
  docs/strictdoc_04_release_notes.sdoc following the existing SDG playbook.
  Not for commit/PR titles and descriptions themselves — see the
  commit-message skill for those. Not for docs/*.sdoc feature documentation
  — see the feature-docs skill for that.
---

# Release notes

Target file: `docs/strictdoc_04_release_notes.sdoc`.

Trigger: an explicit request, or offered proactively when the user asks for
a PR title/description for a non-trivial change — see "Also consider" in the
commit-message skill. Don't try to guess "the task is done" any other way;
the user decides that, and asking for PR text is how that decision shows up.

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

## Before writing

This file is a `.sdoc` file. Follow `sdoc-conventions` (line width, no
hand-authored `MID`, matching existing structure).

## Before returning the result

Run `doc-voice` on the drafted text and apply its findings before presenting
the result.
