// @relation(REQ-1, scope=file)

/**
 * @relation(REQ-2, scope=function, role=Implementation)
 * @relation(REQ-1, scope=function, role=Test)
 */
void foo() {
  // foo
  // comment comment comment comment comment comment comment comment comment comment comment
}

// @relation(REQ-3, scope=range_start)
void bar() {
  // bar
}
// @relation(REQ-3, scope=range_end)

void someFunc() {
  // someFunc
}

// @relation(REQ-3, scope=function)
void longFunctionName() {
  // boo
  // boo
  // boo
  // boo
  // @relation(REQ-4, scope=range_start)
  // boo
  // boo
  // boo
  // boo // @relation(REQ-1, scope=line)
  // boo
  // boo
  // @relation(REQ-4, scope=range_end)
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
  // boo
}
