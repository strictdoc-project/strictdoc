---
name: commit-message
description: |
  Use when the user asks for a commit title/message, or for a PR title and
  description. These are two separate requests for two separate outputs,
  triggered independently — a commit message is proposed per commit; a PR
  title/description is proposed when the user considers the work done and
  ready to open a PR. They may end up similar in a 1-commit-per-PR change,
  but never assume they're the same text. This skill only drafts text — it
  never runs `git commit` or `gh pr create`; the user commits and opens PRs
  themselves. Not for release notes — see the release-notes skill for
  docs/strictdoc_04_release_notes.sdoc entries, and offer that skill
  alongside this one whenever a PR title/description is requested (see
  "Also consider" below).
---

# Commit message / PR title and description

Two distinct outputs, drafted on request, never executed by the agent:

- **Commit message** — requested for a specific commit, while work is
  ongoing.
- **PR title and description** — requested when the user considers the work
  done and is ready to open a PR. This request is the reliable signal that a
  task is finished; nothing else reliably tells the agent that.

Draft only the one asked for. Don't assume the PR text reuses the last
commit message just because this repo prefers 1 commit per 1 PR — check
whether the diff or scope has moved on since that commit before reusing any
of its wording.

## Title

Applies to both the commit title and the PR title — same format either way.
Specified in the SDG (`docs/strictdoc_11_developer_guide.sdoc`, section "Git
workflow"): Conventional Commits.

```
<type>(<optional scope>): <description>
```

- `scope` is a major feature area or a folder. Comma-separate if the work
  spans more than one: `refactor(server, UI): update to new requirement
  styles`.
- A `<type>(scope): <subscope>: <description>` form is also allowed.
- Examples from the SDG, follow this register:
  ```
  feat(html2pdf): add a new option to force page breaks
  fix(backend/sdoc_source_code): add Rust support
  refactor(cli): migrate "import excel" to command pattern
  chore(cli): rename shared.py -> _shared.py
  docs: update release notes
  ```
- `type` reflects what the change actually is (`feat`, `fix`, `refactor`,
  `chore`, `docs`, `test`, ...), not a generic label. Pick the type future
  release-notes filtering depends on: only `feat:` and `fix:` commits get
  summarized into release notes, so mislabeling a user-facing change as
  `chore` or `refactor` hides it from that process.

## Description / body

Applies to both the commit body and the PR description.

Result — stated as one fact, action verb, past tense, no lead-up. Mechanism
and reason — the concrete thing that changed (an actual event, function, or
entity, not an abstraction like "changed the logic") and why, in one clause:
"because X needed Y."

Forbidden: "was/became" before/after framing, testing details, bug or
investigation history, any trailing "let me know if..." closer.

## Also consider

When drafting a PR title/description — not a plain commit message — and the
change looks non-trivial (per the contributor checklist in
`docs/strictdoc_10_contributing.sdoc`), also offer to draft a release notes
entry via the release-notes skill. This is the point in the workflow where
"is this done" is actually known, so it's the right moment to raise it, not
something to guess earlier.

## Before returning the result

Run `doc-voice` on the drafted text and apply its findings.
