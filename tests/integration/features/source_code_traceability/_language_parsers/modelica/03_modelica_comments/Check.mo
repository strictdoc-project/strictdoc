// @relation(REQ-1, scope=file)
within Rig;
model Check
  Real y;
  Real z;
equation
  /* @relation(REQ-2, scope=range_start) */
  y = 1;
  // @relation(REQ-2, scope=range_end)
  // @relation(REQ-3, scope=line)
  z = 2;
end Check;
