within ;
package Rig "A test rig"
  model Check "Checks of a test case"
    Real req1Check "Rise check";
    Real req2Check(start = 0) "Fall check";
  equation
    req1Check = 1;
    der(req2Check) = 1;
  end Check;
  type Temperature = Real(unit = "K") "A short class";
end Rig;
