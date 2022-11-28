Contributing to StrictDoc
$$$$$$$$$$$$$$$$$$$$$$$$$

Contributions to StrictDoc are welcome and appreciated. StrictDoc is based on
Python and maintained as any other Python package on GitHub: with linting,
tests, and hopefully enough best practice put into the codebase.

The rules described below is the summary of what is considered to be the
currently preferred development style for StrictDoc. These rules have been
relatively stable for quite a while but any rule can still be changed if a
better development practice is found.

Any feedback on this contributing guideline is appreciated.

Contributor checklist
=====================

This is a condensed checklist that summarises the information presented in the
rest of this guideline.

Before opening your Pull Request, please make sure to:

1. Run ``invoke check`` tasks locally. This task calls several lint and test
   scripts and it is the very task that is run by the GitHub CI process.
2. A contribution that contains changes to the StrictDoc's codebase shall also
   include tests that exercise the changed behavior. A contribution without any
   tests is unlikely to be accepted (with the exception of "code climate"
   changes, see `Python code`_ below).
3. Follow the conventions of the section "Git workflow" (see
   `Git workflow`_). A clean Git history and conventional
   commit names are expected for every single contribution.

Python code
===========

- The version of Python is set to be as low as possible given some constraints
  of StrictDoc's dependencies. Ideally, the lowest Python version should only be
  raised when it is consistently deprecated by major software platforms like
  Ubuntu or GitHub Actions.

- All developer tasks are collected in the `tasks.py` which is run by Invoke
  tool. Run the ``invoke --list`` command to see the list of available commands.

- Formatting is governed by `black` which reformats the code automatically
  when the ``invoke check`` command is run.

  - If a string literal gets too long, it should be split into a multiline
    literal with each line being a meaningful word or subsentence.

- If a contribution includes changes in StrictDoc's code, at least the
  integration-level tests should be added to the `tests/integration`. If the
  contributed code needs a fine-grained control over the added behavior, adding
  both unit and integration tests is preferred. The only exception where a
  contribution can contain no tests is "code climate" which is work which
  introduces changes in code but no change to the functionality.

Git workflow
============

- The preferred Git workflow is "1 commit per 1 PR". If the work truly deserves
  a sequence of commits, each commit shall be self-contained and pass all checks
  from the ``invoke check`` command. The preferred approach: split the work into
  several independent Pull Requests to simplify the work of the reviewer.

- The branch should be always rebased against the main branch. The
  ``git fetch && git rebase origin/main`` is preferred over
  ``git fetch && git merge main``.

- The Git commit message should follow the format: `context: description` where
  the context can be a major feature being added or a folder. A form of
  `context: subcontext: description` is also an option. Typical examples:

  - `docs: fix links to the grammar.py`
  - `reqif: native: export/import roundtrip for multiline requirement fields`
  - `backend/dsl: switch to dynamic fields, with validation`
  - `Poetry: add filecheck as a dependency`

- When a contribution is simply an improvement of existing code without a change
  in the functionality, the commit should be named: `Code climate: description`.

  - Example: `Code climate: fix all remaining major Pylint warnings`.

Documentation
=============

- Every change in the functionality or the infrastructure should be documented.
- Every line of documentation shall be no longer than 80 characters. StrictDoc's
  own documentation has a few exceptions, however, the latest preference is
  given to 80 characters per line. Unfortunately, until there is automatic
  support for mixed SDoc/RST content, all long lines shall be edited and
  split by a contributor manually.
- The ``invoke sphinx`` task should be used for re-generating documentation on a
  developer machine.

