package body Hello is
   -- Some text.
   --
   -- @relation(REQ-1, scope=function)
   procedure Hello_World_1;

   -- Some text.
   --
   -- @relation(REQ-2, scope=function)
   procedure Hello_World_2;

   -- Some text.
   procedure Hello_World_1 is null;

   -- Some text.
   procedure Hello_World_2 is
   begin
      Hello_World_1;
   end Hello_World_2;
end Hello;
