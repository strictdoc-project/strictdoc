// @relation(REQ-1, scope=file)

/**
 * @relation(REQ-2, scope=function)
 * @relation(REQ-1, scope=function)
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

// @relation(REQ-3, scope=function)
void boo() {
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
