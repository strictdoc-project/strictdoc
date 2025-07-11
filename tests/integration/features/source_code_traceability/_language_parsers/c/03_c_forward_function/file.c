#include <stdio.h>

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
void hello_world(void) {
    print("hello world\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2, scope=function)
 */
void hello_world_2(void) {
    print("hello world\n");
}

/**
 * Some text.
 *
 * @relation(REQ-1, REQ-2, scope=function)
 */
void hello_world_3(void) {
    print("hello world\n");
}

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 * @relation(REQ-2, scope=function)
 */
void hello_world_4(void) {
    print("hello world\n");
}
