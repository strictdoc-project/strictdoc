package body Hello is
   package body Inner is
      -- @relation(REQ-1, scope=function)
      procedure Hello_World_1 is null;
   end Inner;

   procedure Outer is
      -- @relation(REQ-2, scope=function)
      function Hello_World_2 return Integer is (2);
   begin
      null;
   end Outer;
end Hello;
