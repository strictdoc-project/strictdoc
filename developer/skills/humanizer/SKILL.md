---
name: humanizer
description: |
  Mandatory pass for any text this agent writes into a project artifact:
  commit messages, PR descriptions, documentation, code comments, task
  files, chat replies saved to a file, anything shipped. Strips
  AI-writing tells. Required project-wide per AGENTS.md, not opt-in.
  Also callable directly for ad-hoc cleanup of a drafted passage.
---

# humanizer

Apply `humanizer_upstream.md` in this directory (vendored from
github.com/blader/humanizer, MIT license, see `HUMANIZER_LICENSE`). Read
it in full and apply it.

Every check named in `humanizer_upstream.md` must be executed individually
as its own action, with its result shown. A single overall reading of the
text does not satisfy this requirement. The skill is not complete until
every one of its named checks has been executed this way.

Do not hand-edit `humanizer_upstream.md`. It is a wholesale vendor copy;
project-specific voice rules belong in a separate file a task-specific
skill can add, not in this one. Refresh by re-fetching entirely:

```
curl -s https://raw.githubusercontent.com/blader/humanizer/main/SKILL.md \
  -o developer/skills/humanizer/humanizer_upstream.md
```
