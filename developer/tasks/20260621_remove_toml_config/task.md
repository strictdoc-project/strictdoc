# Replace all legacy TOML config with Python config

## WHAT

Migrate all test fixtures that still use TOML. Only preserve the test that checks the TOML deprecation message.

Everything else must be migrated to Python config.

Do this across all groups of tests: unit, integration, end-to-end.

For those end-to-end tests, whose TOML or Python configs only contain the
`section_behavior` argument and nothing else:
- For each TOML file, remove this config file entirely without migrating them to 
  Python.
- For each Python file, remove this config file entirely.

## WHY

Some time ago, we deprecated TOML config in favour of Python config.

By the end of 2026, we are planning to remove TOML completely.

In the meantime, the AI tools (Codex, Claude) do not realize that TOML is deprecated, and they keep creating test fixtures with TOML, not Python.

We would like to reduce the number of TOML occurrences in the codebase and move forward with Python.
