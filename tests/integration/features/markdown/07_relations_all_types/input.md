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
  **Path**: foo.c
  **Element**: Function
  **ID**: my_function

File relation to C function.

## File relation Python class

**UID**: REQ-FILE-PY

**RELATIONS**:
- **Type**: File
  **Path**: bar.py
  **Element**: Class
  **ID**: MyClass

File relation to Python class.

## File relation Rust no element

**UID**: REQ-FILE-RUST

**RELATIONS**:
- **Type**: File
  **Path**: baz.rs
  **ID**: my_function

File relation to Rust function without element annotation.

## Requirement with multiple relations

**UID**: REQ-MULTI

**RELATIONS**:
- **Type**: Parent
  **ID**: REQ-PARENT
- **Type**: Parent
  **ID**: REQ-PARENT-EXPLICIT-CHILD
- **Type**: File
  **Path**: multi.c
  **ID**: multi_fn

Multiple relations of different types.
