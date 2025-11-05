#include <stdio.h>

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 *
 * INTENTION: Intention...
 *
 * INPUT: This
 *        is
 *        a statement
 *        \n\n
 *        And this is the same statement's another paragraph.
 *
 * EXPECTED_RESULTS: This is a comment.
 */
void test_case_1(void) {
    print("hello world\n");
}

/**
 * Plain documentation, no fields. Don't auto-generate a SDoc node for this function.
 *
 * @relation(REQ-2, scope=function)
 */
void test_case_2(void) {
    print("hello world\n");
}
