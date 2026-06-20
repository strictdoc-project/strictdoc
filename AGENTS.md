# AGENTS.md

## Declaration of compliance

When starting any work, the AI agent shall print a statement of compliance with
AGENTS.md and the SDG.

## Source of truth

Follow the StrictDoc Developer Guide (`SDG`) for all tasks in this repository:
`docs/strictdoc_11_developer_guide.sdoc`.

## Development

When implementing features or making code changes, comply with all rules and
conventions in `SDG`.

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
