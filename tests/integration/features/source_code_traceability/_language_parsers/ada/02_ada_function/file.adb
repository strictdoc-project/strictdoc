with Ada.Text_IO;

package body Hello is
   -- Some text.
   --
   -- @relation(REQ-1, scope=function)
   procedure Hello_World is
   begin
      Ada.Text_IO.Put_Line ("hello world");
   end Hello_World;

   -- Some text.
   --
   -- @relation(REQ-2, scope=function)
   procedure Hello_World_2 is
   begin
      Ada.Text_IO.Put_Line ("hello world");
   end Hello_World_2;

   -- Some text.
   --
   -- @relation(REQ-1, REQ-2, scope=function)
   procedure Hello_World_3 is
   begin
      Ada.Text_IO.Put_Line ("hello world");
   end Hello_World_3;

   -- Some text.
   --
   -- @relation(REQ-1, scope=function)
   -- @relation(REQ-2, scope=function)
   procedure Hello_World_4 is
   begin
      Ada.Text_IO.Put_Line ("hello world");
   end Hello_World_4;
end Hello;
