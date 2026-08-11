---
name: feature-docs
description: |
  Use when writing or editing text for a task: developer task artifacts
  (task.md, developer/tasks/<task_id>/Context.md, code comments) during
  active work, or the project's user-facing documentation (docs/*.sdoc) when
  documenting a new or changed feature. Two modes with different bars — see
  below. Not for release notes or PR descriptions; see the release-notes
  skill for those.
---

# Feature documentation

Work out which mode applies before writing. The bar is deliberately
different between them — do not apply the "doc" bar to working artifacts, it
is wasted effort and slows down iteration; do not apply the "draft" bar to
shipped documentation, it will read as unpolished.

## Mode: draft — task.md, Context.md, code comments

Bar: the SDG's "Technical writing" section
(`docs/strictdoc_11_developer_guide.sdoc`) only — Bottom Line Up Front,
active voice. Nothing more elaborate than that at this stage.

For `task.md`, follow the WHAT / WHY / HOW structure in
`developer/tasks/task.template.md`. Document the final system's behavior,
requirements, and the chosen approach — not the process that produced it.
Rejected alternatives, false starts, "first I tried X then Y", who found what
and when: none of that belongs here even if true and useful in the moment.
It rots fast and isn't what a future reader needs.

If the user's own notes contain an aside flagged as guidance for you rather
than content ("this is for you, not for the doc" or similar), treat it as an
instruction shaping tone/scope — never paraphrase it into the document, not
even softened.

Do not run a full `doc-voice` pass here; it's working memory, not a
deliverable, and the SDG bar above is sufficient.

## Mode: doc — docs/*.sdoc

Higher bar: this ships to users.

1. Before writing, read 2-3 neighboring sections in the target `.sdoc` file.
   Match existing grammar conventions (`SECTION`/`TEXT` nesting) and the
   terminology already established for the feature area. Do not hand-author
   `MID` values — StrictDoc generates them; follow the SDG's guidance on
   this.
2. Write the addition or edit. Describe what the feature does and how to use
   it now — not how it was built, not what it used to do, not implementation
   history.
3. Run `doc-voice`'s full check (hard rules + style profile, once it exists +
   reference examples) on the result before presenting it.

## Both modes

Never state a requirement, UI behavior, or config default that hasn't been
verified against the actual code or confirmed by the user. If unverified,
say so and ask rather than writing it as fact.
