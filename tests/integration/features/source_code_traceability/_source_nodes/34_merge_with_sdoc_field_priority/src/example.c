#include <stdio.h>

/**
 * DETAIL: detail from source
 */
void example_title_fallback(void) {
    printf("hello world\n");
}

/**
 * DETAIL: detail from source
 */
void example_title_static_wins(void) {
    printf("hello world\n");
}

/**
 * DETAIL: detail from source (wins over stub)
 */
void example_field_source_overrides_stub(void) {
    printf("hello world\n");
}

/**
 * UID: SRC-NODES-BASE/src/example.c/example_field_preserved_when_absent_in_source
 */
void example_field_preserved_when_absent_in_source(void) {
    printf("hello world\n");
}
