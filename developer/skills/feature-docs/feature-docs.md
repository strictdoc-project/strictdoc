---
name: feature-docs
description: |
  Use when writing or editing text for a task: developer task artifacts
  (task.md, developer/tasks/<task_id>/Context.md, code comments) during
  active work, or the project's user-facing documentation (docs/*.sdoc) when
  documenting a new or changed feature. Two modes with different bars — see
  below. Not for release notes; see the release-notes skill. Not for commit
  or PR titles/descriptions; see the commit-message skill.
---

# Feature documentation

Work out which mode applies before writing. The bar is deliberately
different between them — do not apply the "doc" bar to working artifacts, it
is wasted effort and slows down iteration; do not apply the "draft" bar to
shipped documentation, it will read as unpolished.

## Mode: draft — task.md, Context.md, code comments

Bar: the two rules below, from the SDG's "Technical writing" section
(`docs/strictdoc_11_developer_guide.sdoc`). Nothing more elaborate than that
at this stage — no `doc-voice` pass, see why at the end of this mode.

**Bottom Line Up Front (BLUF).** Open with the conclusion, decision, or
result, then the supporting detail — not the other way round. A reader who
stops after the first sentence should already know the outcome. Concretely:
don't open a section with background, context, or the investigation that led
somewhere; open with what is true/decided/done, then explain why if needed.

**Active voice.** Name who or what did the action instead of a passive
construction, e.g. "The engineer linked the requirement to the test case,"
not "The requirement was linked to the test case." Use passive only when the
actor is genuinely unknown or irrelevant to the point being made.

For `task.md`, follow the three-section structure in
`developer/tasks/task.template.md` (read it for the exact scaffold):

- **WHAT** — the expected system behavior, requirements, constraints, and
  success criteria. What must be true when this is done. Not how it's
  implemented.
- **WHY** — the context, motivation, user need, or problem being solved. Not
  the solution.
- **HOW** — the chosen technical approach, opening with a BLUF summary of the
  implemented solution, then architecture, design decisions, and trade-offs.

Across all three sections: document the final system's behavior,
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

1. Follow `sdoc-conventions` before writing: it covers matching existing
   structure, line width, and MID handling for any `.sdoc` edit.
2. Write the addition or edit. Describe what the feature does and how to use
   it now — not how it was built, not what it used to do, not implementation
   history. Every change to functionality or infrastructure should end up
   documented somewhere — don't skip a doc update because nobody asked for
   it explicitly, if the feature-docs skill was invoked for this change.
3. Run `doc-voice`'s full check (hard rules + style profile, once it exists +
   reference examples) on the result before presenting it.
4. Follow `sdoc-conventions`' "After writing" step (`invoke docs`) once done.

## Both modes

Never state a requirement, UI behavior, or config default that hasn't been
verified against the actual code or confirmed by the user. If unverified,
say so and ask rather than writing it as fact.
