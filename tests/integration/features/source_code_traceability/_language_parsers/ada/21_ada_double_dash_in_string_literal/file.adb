package body Hello is
   Label : constant String := "-- @relation(REQ-2, scope=file)";

   -- @relation(REQ-1, scope=function)
   procedure Hello_World is
      Text : constant String := "-- @relation(REQ-2, scope=line)";
   begin
      null;
   end Hello_World;
end Hello;
