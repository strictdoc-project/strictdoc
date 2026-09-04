# AGENTS.md

## Declaration of compliance

MANDATORY FIRST ACTION. NO EXCEPTIONS.

Before calling any tool or writing any response content, your very first text
output MUST be a statement of compliance with AGENTS.md and the SDG.

Do not search files, do not call tools, do not answer the user's question first.
Print the compliance statement first. Then proceed.

If you are reading this and have not yet printed the compliance statement: stop,
print it now, then continue.

## Fork context

This repository (`Robotics010/strictdoc`) is a fork of `strictdoc-project/strictdoc`,
repurposed as a System Engineering tool for a student robotics course (a Eurobot
mobile robot). It is not the upstream open-source project, and work here serves the
course, not upstream's own user base.

The SDG's engineering, testing, and technical-writing conventions still apply as
written, and the SDG remains read-only (see "General rule" below). However, the SDG
describes itself as the guide for "a StrictDoc developer/contributor" and some of its
sections assume upstream's own context: publishing to PyPI, opening pull requests
against `strictdoc-project` for outside review, and upstream's own release process.
Where a SDG section like that conflicts with how this fork actually operates, this
fork's own files (this section, README.md, NOTICE) take precedence — flag the
conflict per "General rule" rather than silently importing upstream's assumption.

`docs/strictdoc_24_development_plan.sdoc` and `docs/strictdoc_28_Backlog.sdoc`
describe `strictdoc-project`'s own multi-year roadmap and backlog (Capella/STPA
integration, LSP, WYSIWYG editing, multi-user accounts, and so on). They are
reference-only for this fork. Never treat a `STATUS: Backlog` entry in either
document as work to pick up here — this fork's priorities come from the user and
from `developer/tasks/eurobot/`.

## Source of truth

Follow the StrictDoc Developer Guide (`SDG`) for all tasks in this repository:
`docs/strictdoc_11_developer_guide.sdoc`.

## Development

When implementing features or making code changes, comply with all rules and
conventions in `SDG`.

## Technical writing

Follow the technical writing guidelines in the StrictDoc Developer Guide.

Before presenting any text written into a project artifact (commit
messages, PR descriptions, docs, code comments, task files, or similar),
apply `developer/skills/humanizer/SKILL.md`. This applies regardless of
which skill, if any, is used for the task.

Translate any user-facing text you write into Russian, since the students
using this tool are not assumed to read English: error/warning messages,
UI labels, and similar strings that end up displayed to a student in the
app. This does not apply to code, identifiers, code comments, commit
messages, or logs meant for developers — those stay in English per the
rest of this section.

## Skills

Reusable instructions for writing tasks (release notes, commit/PR text,
task docs, feature docs) live in `developer/skills/<name>/SKILL.md`.
After any change to a skill, regenerate the Claude/Codex pointer stubs:

    python developer/skills/install_skills.py

## Development tasks

When requested by a user to work on a task defined in
`developer/tasks/<task_id>/*.md`, follow the task instructions while fully
respecting the `SDG`.

For agent working memory, use `developer/tasks/<task_id>/Context.md`.

- `Context.md` is working memory only and is not a source of truth.
- Read `developer/tasks/<task_id>/Context.md` if it exists before substantial
  work. If it does not exist, create and populate it with the initial context.
- Keep it current while working.
- Assume the context file is shared with other agents.
- Treat user instructions, `SDG`, and repository files as the source of truth.
- Use it only for the current session context such as status, findings, decisions,
  blockers, and open questions.

Do not modify files in `developer/tasks/<task_id>/` unless the user explicitly
requests it. Those files are task artifacts intended for the user;
`developer/tasks/<task_id>/Context.md` is the only agent-maintained file.

New course-specific task work is filed under
`developer/tasks/eurobot/<date>_<slug>/`, using the same `task.template.md`
structure and the same `Context.md` convention described above. The existing
flat, date-prefixed folders directly under `developer/tasks/` (several carrying
upstream GitHub issue numbers, e.g.
`20260621_add_node_on_empty_table_screen_2957`) are inherited upstream task
history, kept for reference. They are not this fork's queue and are not
extended going forward.

## Code review

- When performing code review, evaluate changes strictly against `SDG`.
- Flag any deviations from the guide.

## General rule

- In case of uncertainty, default to `SDG`.
- In case of deviations from the guide, flag them to the developer.
- `SDG` is read-only and shall not be modified by agents.

## Agent behavior

- Ask for clarification when missing details could materially affect behavior,
  interfaces, safety, scope, or user-visible outcomes.
- Do not invent requirements or assumptions; verify against user instructions,
  `AGENTS.md`, `SDG`, and repository contents, and stop if they conflict.
- Stay within the requested scope; ask before deleting files, changing public
  interfaces, or performing broad refactors.

## Change scope

- Do not modify shared components for a local feature unless explicitly
  approved by the user.
- Prefer feature-local templates, scripts, and styles.
- If changing a shared component appears necessary, stop and request approval
  before editing it.

## Testing

- Prefer `invoke test-*` commands for all test commands. Only resort to
running the test commands directly if not possible with Invoke tasks.
- Always run end-to-end tests with `--headless`.
- Do not create throw-away "smoke tests". If such a smoke test is needed,
create proper unit, integration or end2end tests.
