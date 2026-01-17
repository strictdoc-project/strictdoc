#![doc = " Top-level module"]
#![doc = " @relation(REQ-INNER-DOC-ATTR)"]

#![feature(extern_types, trait_alias)]

pub trait Processor {
    type Output;
    const MAX_SIZE: usize;

    fn process(&self, input: &str) -> Self::Output;

    fn validate(&self) -> bool {
        #![doc = " Default method with"]
        #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
        #![doc = " Description: validation check routine"]

        true
    }
}

pub trait ProcessorClone = Processor + Clone;

pub struct Container {
    pub name: String,
    value: i32,
}

impl Processor for Container {
    type Output = String;
    const MAX_SIZE: usize = 1024;

    fn process(&self, input: &str) -> Self::Output {
        #![doc = " Impl method with"]
        #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
        #![doc = " Description: implementation of a process"]

        format!("{}: {}", self.name, input)
    }
}

impl Container {
    #![doc = " Inherent impl with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Text: inherent method block"]

    pub fn new(name: String) -> Self {
        #![doc = " Inherent method with"]
        #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
        #![doc = " Words: constructor function pattern"]

        Self { name, value: 0 }
    }

    pub fn get_value(&self) -> i32 {
        #![doc = " Another method with"]
        #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
        #![doc = " Random: getter accessor method"]

        self.value
    }
}

pub fn process_data(input: &str) -> String {
    #![doc = " Function with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Description: top-level function utility"]

    input.to_uppercase()
}

pub async fn async_process(data: Vec<u8>) -> Result<(), std::io::Error> {
    #![doc = " Async function with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Random: asynchronous operation handler"]

    Ok(())
}

pub const fn compute_magic(x: u32) -> u32 {
    #![doc = " Const function with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Text: compile-time evaluable function"]

    x * 42
}

pub unsafe fn dangerous_operation(ptr: *mut u8) {
    #![doc = " Unsafe function with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Words: unchecked operation wrapper"]

    if !ptr.is_null() {
        *ptr = 0;
    }
}

pub mod submodule {
    #![doc = " Module with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Description: nested module container"]

    pub struct Inner {
        data: Vec<u8>,
    }
}

extern "C" {
    #![doc = " Foreign function interface with"]
    #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
    #![doc = " Text: external C interface block"]

    fn external_func(x: i32) -> i32;

    static EXTERNAL_VAR: i32;

    type OpaqueType;
}

mod tests {
    #[test]
    fn test_basic() {
        #![doc = " Test function with"]
        #![doc = " @relation(REQ-INNER-DOC-ATTR)"]
        #![doc = " Random: unit test case definition"]

        assert_eq!(2 + 2, 4);
    }
}
