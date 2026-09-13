---
name: asd-ste100
description: |
  Use when English text must be parsed without a human to resolve
  ambiguity: tool descriptions, error messages, inter-agent instructions,
  system prompts, status reports. Also use when text reads as dense,
  hedged, or easy to misparse. Triggers: disambiguate, STE100 rewrite,
  apply Simplified Technical English, plain-language rewrite,
  controlled-language rewrite. Not for creative or marketing copy.
---

# asd-ste100

Apply `asd_ste100_upstream.md` in this directory (vendored from
github.com/danyuchn/asd-ste100-skill, MIT license, see
`ASD_STE100_SKILL_LICENSE`). Read it in full and follow it.

This directory intentionally keeps only the upstream `SKILL.md` content
and its license, not the upstream repository's `references/`, `examples/`,
or `scripts/` directories. `asd_ste100_upstream.md` has been edited to
remove the parts of the upstream text that pointed to those directories,
so it is not a byte-for-byte vendor copy.

Refresh by re-cloning the upstream repository, copying its `SKILL.md` and
`LICENSE` over these two files, and re-applying the removal of the
`references/`, `examples/`, and `scripts/` mentions.
