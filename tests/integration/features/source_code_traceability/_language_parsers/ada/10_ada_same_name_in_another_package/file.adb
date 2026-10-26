with Ada.Text_IO;

package body Hello is
   -- Some text.
   procedure Hello_World_1 is
   begin
      Ada.Text_IO.Put_Line ("Hello world 1");
   end Hello_World_1;

   -- Some text.
   function Hello_World_2 return Integer is (2);
end Hello;
