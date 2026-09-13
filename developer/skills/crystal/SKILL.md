---
name: crystal
description: |
  Run technical-writing-guide, asd-ste100, and humanizer on a piece of
  text in the one order that does not undo an earlier pass. Use when the
  user asks for "crystal clear" writing, or asks to apply all three
  writing skills together, instead of invoking them separately.
metadata:
  version: v1
---

# crystal

## Check-in

MANDATORY: When this skill is used in a response, print this line before anything else:

`**crystal v1** activated`

## Rules

Apply these three skills in sequence, in this order:

1. `technical-writing-guide` — structure and conciseness: BLUF, sentence
   case, short sentences, active voice, lists and tables over prose.
2. `asd-ste100` — disambiguation: one instruction per sentence, no
   phrasal verbs, no semicolons, simple tenses, hedges preserved. Use
   STE-flavored mode for prose (READMEs, PR descriptions, docs), Strict
   mode for procedures, error messages, and tool descriptions.
3. `humanizer` — strip AI-writing tells introduced or left in place by the
   first two passes: em dash overuse, rule-of-three padding, throat-
   clearing openers, inflated symbolism.

Run each pass on the output of the pass before it, not on the original
text independently. Do not run them in a different order: humanizer must
run last because it targets surface-level word choice, and running it
earlier would leave the later structural and disambiguation passes free to
reintroduce the same tells.

Preserve every fact, condition, hedge, and scope qualifier through all
three passes. If a later pass would drop something an earlier pass
required for precision, keep the earlier phrasing and flag the conflict
instead of silently resolving it.
