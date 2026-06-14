# Add REVERSE_ROLE as optional grammar metadata for Parent/Child relations

## WHAT

Implements proposed support for feature request #2755 by adding REVERSE_ROLE as optional grammar metadata for Parent/Child relations:

Example:
```
RELATIONS:
- TYPE: Parent
  ROLE: Refines
  REVERSE_ROLE: Refined by
```

## WHY

Currently, the defined ROLE name is used for both the forward and backward directions of a relationship. While users can infer the meaning by checking if the relation is a "Parent" or "Child," it creates a mental hurdle. This feature allows the user to optionally define a name for the reverse role, to be presented when the relationship is viewed from the other direction.

## HOW

### Proposed behavior

- ROLE remains the canonical relation identity.
- REVERSE_ROLE is display-only metadata.
- Node-level RELATIONS: stay unchanged.
- Validation/filtering/querying still use (TYPE, ROLE).
- The canonical traceability graph edge remains ROLE. REVERSE_ROLE is only resolved at display time.
- When rendering the relation in the stored direction, StrictDoc shows ROLE.
- When rendering the same relation from the opposite side, StrictDoc shows REVERSE_ROLE if configured.
- If REVERSE_ROLE is not configured, rendering falls back to ROLE, preserving current behavior.
- REVERSE_ROLE is rejected unless ROLE is also specified.

### Implementation details
- Extend the SDoc grammar parser for optional REVERSE_ROLE on Parent/Child grammar relations.
- Add reverse_relation_role to grammar relation model classes.
- Preserve REVERSE_ROLE in the SDoc writer so custom grammars round-trip correctly.
- Add semantic validation for REVERSE_ROLE without ROLE.
- Add traceability-index helpers that resolve the display label based on direction.
- Update relation display in document relation links and diff/changelog views.
- No support in the web grammar editor (at least not in the first PR).
- Add user documentation for REVERSE_ROLE in the StrictDoc user guide.

### Future work

- Add support in the web grammar editor for creating/editing REVERSE_ROLE.
- Decide whether REVERSE_ROLE should be supported for File relations.
- Decide whether ReqIF/JSON/other exports should expose REVERSE_ROLE metadata or ignore it.
- Review other visualizations, such as deep traceability / graph-oriented views, and add reverse role labels where those views render relation role text.

### Verification

- Parser/writer round-trip for REVERSE_ROLE
- Parser support for REVERSE_ROLE in external .sgra grammar files.
- Validation failure for REVERSE_ROLE without ROLE.
- Display behavior for both Parent-defined and Child-defined relations.
- Fallback behavior for both Parent-defined and Child-defined relations when REVERSE_ROLE is omitted.
