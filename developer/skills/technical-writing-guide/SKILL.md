---
name: technical-writing-guide
description: |
  Rules and DO/AVOID examples for writing terse, well-structured technical
  documentation: BLUF, sentence case, active voice, concise wording, and
  structure over prose. Use when writing or editing technical docs,
  READMEs, specs, or reviewing text for clarity and conciseness.
---

# technical-writing-guide

Apply `technical_writing_guide_upstream.md` in this directory (vendored
from github.com/strictdoc-project/technical_writing_skill). Read it in
full and follow it, including its check-in line and its mandatory final
re-pass over any text this agent rewrote.

Do not hand-edit `technical_writing_guide_upstream.md`. It is a wholesale
vendor copy. Refresh by re-fetching entirely:

```
curl -s https://raw.githubusercontent.com/strictdoc-project/technical_writing_skill/main/SKILL.md \
  -o developer/skills/technical-writing-guide/technical_writing_guide_upstream.md
```
