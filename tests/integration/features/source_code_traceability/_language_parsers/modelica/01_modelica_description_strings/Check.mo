within Rig;
model Check "Checks of TC-1 @relation(TC-1, scope=class)"
  parameter Real k = 1 "Gain";
  Real y "Output";
  Real req1Check
    "Rise check @relation(REQ-1, scope=component)";
  Real req2Check, req3Check "Fall checks @relation(REQ-2, REQ-3)";
equation
  y = k;
  req1Check = y;
  req2Check = y;
  req3Check = y;
end Check;
