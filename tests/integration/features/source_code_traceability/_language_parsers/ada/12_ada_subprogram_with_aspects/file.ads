package Hello is
   -- @relation(REQ-1, scope=function)
   procedure Hello_World_1
     with Inline;

   -- @relation(REQ-2, scope=function)
   generic
      type Item is private;
   procedure Swap (Left, Right : in out Item);

   -- @relation(REQ-2, scope=function)

   procedure Hello_World_3;
end Hello;
