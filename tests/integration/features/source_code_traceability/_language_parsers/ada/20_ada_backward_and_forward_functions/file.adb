-- @relation(REQ-1, scope=file)

package body Hello is
   -- @relation(REQ-2, scope=function, role=Implementation)
   -- @relation(REQ-1, scope=function, role=Test)
   procedure Foo is
   begin
      null;
   end Foo;

   -- @relation(REQ-3, scope=range_start)
   procedure Bar is
   begin
      null;
   end Bar;
   -- @relation(REQ-3, scope=range_end)

   procedure Some_Func is null;

   -- @relation(REQ-3, scope=function)
   procedure Long_Function_Name is
   begin
      -- boo
      -- @relation(REQ-4, scope=range_start)
      -- boo
      Some_Func; -- @relation(REQ-1, scope=line)
      -- boo
      -- @relation(REQ-4, scope=range_end)
      -- boo
   end Long_Function_Name;
end Hello;
