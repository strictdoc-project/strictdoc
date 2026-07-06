# Make Markdown markup convention more consistent

## WHAT

In all Markdown-related code and specs change:

- `RELATIONS` shall be renamed to `Relations` which is from now on the new baseline.
- `Reverse Role` shall always be `Reverse role`.

Currently, SDMarkdownReader always upper-cases parsed field names. Remove this behavior completely. A user shall be free to choose whether they work with:
  - `ALL_CAPS` or `Camel-Case` or `Camel Case` node field titles.
  - The field names are constrained by the user grammar and nothing else.
- Update code, specs, and tests to reflect these changes.

Remove the ALL_CAPS hardcoding or uppercasing from everywhere.

The `UID`/`MID` stay as abbreviations but things like `PREFIX` -> `Prefix`, `VERSION` -> `Version`, `DATE` -> `Date` etc.

Update the spec/ folder's Markdown grammar and files to follow the new convention, i.e., `TITLE` -> `Title`, `STATEMENT` -> `Statement`, `RATIONALE` -> `Rationale`.

### New default grammar fields

Make default grammar fields to be:

- MID
- UID
- Level
- Status
- Tags
- Title
- Statement
- Rationale
- Comment
- Relations

### Human titles are not affected

Don't remove the handling of human titles. A user may still want to customize their titles for displaying them differently in the UI.

## WHY

Compared to the SDoc conventions, where the `ALL_CAPS` style is used everywhere,
we want maximum readability and ease-of-use for Markdown. The WHAT changes are
supposed to bring Markdown a little away from SDoc/ALL_CAPS style adding
better readability.

## HOW

- If present, highlight conflicts in this task given the existing implementation.
