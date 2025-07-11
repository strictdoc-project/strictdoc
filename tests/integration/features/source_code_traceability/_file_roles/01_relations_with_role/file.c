// @relation(REQ-001, scope=function, role=Implementation)
extern int extfoo();

int extfoo() {
    return 0;
}

static void foo();

int main() {
    foo();  // @relation(REQ-001, scope=line, role=Implementation)
    return 0;
}

// @relation(REQ-001, scope=function, role=Implementation)
static void foo() {}

// @relation(REQ-001, scope=range_start, role=Implementation)
static void bar1() {}
static void bar2() {}
// @relation(REQ-001, scope=range_end)
