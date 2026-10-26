procedure Hello_World is
begin
   -- @relation(REQ-1, scope=range_start)
   Ada.Text_IO.Put_Line ("hello world");
   -- @relation(REQ-1, scope=range_end)
end Hello_World;
