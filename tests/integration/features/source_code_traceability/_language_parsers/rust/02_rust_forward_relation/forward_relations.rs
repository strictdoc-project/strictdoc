mod foo_module {
    pub trait FooTrait {
        fn foo(&self) {}
    }

    fn foo() {
        fn bar() -> u32 {
            pub const BAR_CONST: u32 = 42;
            BAR_CONST
        }

        println!("{}", bar());
    }
}

struct FooTuple(i32);

impl foo_module::FooTrait for FooTuple {
    fn foo(&self) {}
}

union FooUnion {a: i32}

pub const FOO_CONST: u32 = 42;

trait FooTrait {
    fn foo() {}
}

pub enum FooEnum {
    Foo,
    Bar {
        baz: u64,
    },
}
