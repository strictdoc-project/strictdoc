# Relations all types

## Parent requirement

**UID**: REQ-PARENT

Parent requirement statement.

## Child requirement

**UID**: REQ-CHILD

**RELATIONS**:
- **Type**: Parent
  **ID**: REQ-PARENT

Child requirement statement.

## Parent with child relation

**UID**: REQ-PARENT-EXPLICIT-CHILD

**RELATIONS**:
- **Type**: Child
  **ID**: REQ-CHILD

Parent with explicit child relation.

## File relation C function

**UID**: REQ-FILE-C

**RELATIONS**:
- **Type**: File
  **Path**: file.c
  **Element**: function
  **ID**: my_function

File relation to C function.

## File relation Python class

**UID**: REQ-FILE-PY

**RELATIONS**:
- **Type**: File
  **Path**: file.py
  **Element**: class
  **ID**: MyClass

File relation to Python class.

## File relation Rust no element

**UID**: REQ-FILE-RUST

**RELATIONS**:
- **Type**: File
  **Path**: file.rs
  **ID**: my_function

File relation to Rust function without element annotation.

## File relation line range

**UID**: REQ-FILE-LINE-RANGE

**RELATIONS**:
- **Type**: File
  **Path**: file.c
  **Lines**: `10, 20`

File relation to a line range.

## Requirement with multiple relations

**UID**: REQ-MULTI

**RELATIONS**:
- **Type**: Parent
  **ID**: REQ-PARENT
- **Type**: Parent
  **ID**: REQ-PARENT-EXPLICIT-CHILD
- **Type**: File
  **Path**: file.c
  **ID**: multi_fn

Multiple relations of different types.
