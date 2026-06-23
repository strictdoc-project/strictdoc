# Extend the Markdown specification to support UID prefixes

## WHAT

Extend the Markdown specification to support node PREFIX.

The PREFIX behavior shall be reflected explicitly:

- In the Markdown specification.
- In the unit tests.
- In the integration tests.
- In the end-to-end tests.

## WHY

The PREFIX field is instrumental when a user wants to have auto-generated
node UIDs with custom prefixes other than the default `REQ-` prefix.

## HOW

