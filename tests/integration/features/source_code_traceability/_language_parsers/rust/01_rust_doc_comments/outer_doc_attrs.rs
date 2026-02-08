#![feature(extern_types, stmt_expr_attributes, trait_alias)]

#[doc = " Top-level const with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " quantum cascade amplifier"]
pub const MAGIC_NUMBER: u32 = 42;

#[doc = " Static item with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " nebula crystalline matrix"]
pub static GLOBAL_STATE: &str = "initialized";

#[doc = " Type alias with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " temporal flux capacitor"]
pub type CustomResult<T> = Result<T, Box<dyn std::error::Error>>;

#[doc = " Struct with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " polymorphic data structure"]
pub struct Container {
    #[doc = " Field doc with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " ethereal quantum state"]
    pub name: String,

    #[doc = " Another field with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " cascading resonance field"]
    value: i32,
}

#[doc = " Enum with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " enumerated variant collection"]
pub enum Status {
    #[doc = " Variant doc with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " active processing node"]
    Active,

    #[doc = " Another variant with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " suspended animation chamber"]
    Idle {
        #[doc = " Field in variant with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        #[doc = " temporal duration metric"]
        duration: u64,
    },

    #[doc = " Tuple variant with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " error state container"]
    Error(
        #[doc = " Tuple field with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        #[doc = " diagnostic error code"]
        i32
    ),
}

#[doc = " Union with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " memory-aligned data union"]
pub union FloatOrInt {
    #[doc = " Union field with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " floating-point representation"]
    f: f32,

    #[doc = " Another union field with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " integer bit pattern"]
    i: i32,
}

#[doc = " Trait definition with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " behavioral interface contract"]
pub trait Processor {
    #[doc = " Associated type with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " output data type"]
    type Output;

    #[doc = " Associated const with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " maximum buffer capacity"]
    const MAX_SIZE: usize;

    #[doc = " Trait method with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " processing operation handler"]
    fn process(&self, input: &str) -> Self::Output;

    #[doc = " Default method with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " validation check routine"]
    fn validate(&self) -> bool {
        true
    }
}

#[doc = " Trait alias with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " combined trait bounds"]
pub trait ProcessorClone = Processor + Clone;

#[doc = " Implementation block with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " trait implementation container"]
impl Processor for Container {
    #[doc = " Impl associated type with"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " Words: concrete output type"]
    type Output = String;

    #[doc = " Impl const with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " size constant value"]
    const MAX_SIZE: usize = 1024;

    #[doc = " Impl method with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " implementation of a process"]
    fn process(&self, input: &str) -> Self::Output {
        format!("{}: {}", self.name, input)
    }
}

#[doc = " Inherent impl with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " inherent method block"]
impl Container {
    #[doc = " Inherent method with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " constructor function pattern"]
    pub fn new(name: String) -> Self {
        Self { name, value: 0 }
    }

    #[doc = " Another method with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " getter accessor method"]
    pub fn get_value(&self) -> i32 {
        self.value
    }
}

#[doc = " Function with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " top-level function utility"]
pub fn process_data(input: &str) -> String {
    input.to_uppercase()
}

#[doc = " Async function with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " asynchronous operation handler"]
pub async fn async_process(data: Vec<u8>) -> Result<(), std::io::Error> {
    Ok(())
}

#[doc = " Const function with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " compile-time evaluable function"]
pub const fn compute_magic(x: u32) -> u32 {
    x * 42
}

#[doc = " Unsafe function with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " unchecked operation wrapper"]
pub unsafe fn dangerous_operation(ptr: *mut u8) {
    if !ptr.is_null() {
        *ptr = 0;
    }
}

#[doc = " External crate import with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " external dependency reference"]
extern crate std;

#[doc = " Module with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " nested module container"]
pub mod submodule {
    //! Inner module doc with random docs:
    //! @relation(REQ-OUTER-LINE-DOC)
    //! module-level documentation

    #[doc = " Nested struct with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " encapsulated data structure"]
    pub struct Inner {
        #[doc = " Field with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        #[doc = " internal state variable"]
        data: Vec<u8>,
    }
}

#[doc = " Foreign function interface with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " external C interface block"]
extern "C" {
    #[doc = " Foreign function with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " C library function binding"]
    fn external_func(x: i32) -> i32;

    #[doc = " Foreign static with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " global C variable reference"]
    static EXTERNAL_VAR: i32;

    #[doc = " Foreign type with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " C type declaration"]
    type OpaqueType;
}

#[doc = " Macro invocation with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " declarative macro call"]
macro_rules! test_macro {
    () => {
        println!("test");
    };
}

#[doc = " Function with match arms containing doc attributes"]
#[doc = " This function demonstrates"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
pub fn match_example(x: Option<i32>) -> i32 {
    match x {
        #[doc = " Match arm with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        #[doc = " some variant pattern"]
        Some(val) => val,

        #[doc = " None arm with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        #[doc = " default fallback case"]
        None => 0,
    }
}

#[doc = " Generic function with random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " parameterized function template"]
pub fn generic_fn<
    #[doc = " Type parameter with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " generic type variable"]
    T: Clone,

    #[doc = " Const parameter with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " compile-time constant value"]
    const N: usize,
>(
    input: [T; N],
) -> Vec<T> {
    input.to_vec()
}

#[doc = " Struct with generic parameters random docs:"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
#[doc = " generic container structure"]
pub struct GenericContainer<
    #[doc = " Lifetime param with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " reference lifetime bound"]
    'a,

    #[doc = " Generic type param with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " primary type parameter"]
    T,
> where
    T: 'a,
{
    #[doc = " Reference field with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " borrowed data reference"]
    pub data: &'a T,
}

#[doc = " Test struct for field value attributes in expressions"]
#[cfg(any(target_os = "linux", target_os = "macos"))]
#[doc = " This demonstrates"]
#[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
pub fn struct_expression_test() {
    let _ = Container {
        #[doc = " Field value with random docs:"]
        #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
        name: String::from("test"),
        value: 42,
    };
}

#[doc = " Test if we can add a docstring to an expression literal"]
fn expr_lit(x: i32) -> i32 {
    #[doc = " Test an expression"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    8675309;
    #[doc = " SURPRISING: We are documenting"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " the first part of the expression, not the entire expression,"]
    #[doc = " see `test_not_surprising` for how to fix this"]
    x + 2
}

fn test_not_surprising(x: i32) -> i32 {
    #[doc = " Test documenting the"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    (x + 2)
}

#[cfg(any(test, doc))]
mod tests {
    #[doc = " Test function with random docs:"]
    #[doc = " @relation(REQ-OUTER-DOC-ATTR)"]
    #[doc = " unit test case definition"]
    #[cfg_attr(not(doc), test)]
    fn test_basic() {
        assert_eq!(2 + 2, 4);
    }
}
