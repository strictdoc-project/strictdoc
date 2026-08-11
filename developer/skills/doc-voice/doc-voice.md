---
name: doc-voice
description: |
  Internal style-and-cleanup layer used by the release-notes and feature-docs
  skills. Strips AI-writing tells and enforces StrictDoc's house voice on any
  text about to ship: release notes, PR descriptions, docs/*.sdoc content.
  Call directly for ad-hoc cleanup of a drafted passage before it ships.
---

# doc-voice

Self-check pass, not a drafting tool. Run it on text someone else (or another
skill) already wrote, right before it ships.

## 1. Hard rules — AI-writing patterns

Apply `humanizer_upstream.md` in this directory (vendored from
github.com/blader/humanizer, MIT license, see `HUMANIZER_LICENSE`). Read it in
full before the check — it defines the patterns, severity, and the
draft/audit/final process.

Do not hand-edit `humanizer_upstream.md`. It is a wholesale vendor copy; local
customization goes in `style_profile.md` instead, so refreshing the vendor
file never clobbers house rules. See "Refreshing the vendor copy" below.

What that file already covers, so this skill doesn't repeat it: inflated
symbolism, promotional language, participial "-ing" tails, rule of three,
"not just X, it's Y" parallelisms, "represents/serves as" hedging around a
plain "is", unnamed authorities ("experts say"), synonym-cycling for a term
that should stay consistent, em dash / bold / emoji overuse, chat leftovers
("hope this helps"). Per that skill's own instructions: judge by density, not
by whether a pattern appears at all — none of these are individually
forbidden in isolation.

## 2. StrictDoc house voice

See `style_profile.md`.

Current status: **not yet built.** Corpus analysis is a separate, explicit
step — see below. Until `style_profile.md` has real content, the only house
rule to enforce is the SDG's own "Technical writing" section
(`docs/strictdoc_11_developer_guide.sdoc`): Bottom Line Up Front, active
voice. Do not invent house-style rules beyond that in the meantime.

## 3. Building style_profile.md

Only do this when the user explicitly asks to build or update the style
profile. Do not trigger it as a side effect of a normal doc-voice pass.

1. Ask the user which existing docs, PRs, or release notes are representative
   of the voice to match. Do not assume — StrictDoc has more than one doc
   author, and their voices differ. Get a corpus of roughly 15-30 texts.
2. Read the corpus. Extract observations backed by quotes from the corpus,
   not adjectives. "Sentences in the User Guide average 12-18 words, rarely
   compound" is usable; "the style is clear and professional" is not.
3. Split findings into three sections inside `style_profile.md`:
   - Hard bans — constructions, words, or formatting confirmed absent from
     the corpus.
   - Allowed and encouraged — habits the corpus shows that a model would
     otherwise sand down out of caution (StrictDoc's terse imperative mood,
     specific technical nouns over paraphrase, etc.).
   - Reference examples — 3-4 corpus passages included verbatim. These
     outrank the abstract rules when the two conflict.
4. Keep genre apart from voice: user-facing docs (`docs/strictdoc_01_*`
   onward), the developer guide, and release notes are different genres even
   when the same person wrote them. Note genre-specific deviations as
   sub-profiles inside the file rather than flattening them into one voice.

## 4. Refreshing the vendor copy

Re-fetch and overwrite wholesale:

```
curl -s https://raw.githubusercontent.com/blader/humanizer/main/SKILL.md \
  -o developer/skills/doc-voice/humanizer_upstream.md
```

Never hand-edit `humanizer_upstream.md` before or after a refresh — anything
StrictDoc-specific belongs in `style_profile.md`, which this refresh never
touches.
