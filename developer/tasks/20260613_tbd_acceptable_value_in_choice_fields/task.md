# Accept "TBD"/"TBC" as valid values in any Single or Multiple Choice field

## WHAT

We would like to relax the Single and Multiple Choice fields validation so that it always treats "TBD" and "TBC" values as acceptable fields.

## WHY

Some grammars may have choice fields set to `REQUIRED: True` in the grammar. At the same time users may not yet have the right field value when creating a choice field via the CLI or web interfaces.

In particular, quick editing in the TABLE screen is much easier when the required fields can be initially created with "TBD"/"TBC" values in them.

## HOW

- Relax the validation in Form Objects and Python model classes, so that every Choice field, single or multiple, accepts "TBD" and "TBC" as acceptable values.
- Update unit, integration, and e2e tests to exercise this new behavior.
