#define MY_ATTR
#define MY_SECTION(name)

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
MY_ATTR void hello_world(void) {
    print("hello world\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2, scope=function)
 */
static MY_ATTR const char * hello_world_2(void) {
    return "hello world\n";
}

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
MY_SECTION(".text") void hello_world_3(void) {
    print("hello world\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2, scope=function)
 */

void hello_world_4(void) {
    print("hello world\n");
}
