#![feature(extern_types, stmt_expr_attributes, trait_alias)]

/**
 * Top-level const with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * quantum cascade amplifier
 */
pub const MAGIC_NUMBER: u32 = 42;

/**
 * Static item with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * nebula crystalline matrix
 */
pub static GLOBAL_STATE: &str = "initialized";

/**
 * Type alias with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * temporal flux capacitor
 */
pub type CustomResult<T> = Result<T, Box<dyn std::error::Error>>;

/**
 * Struct with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * polymorphic data structure
 */
pub struct Container {
    /**
     * Field doc with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * ethereal quantum state
     */
    pub name: String,

    /**
     * Another field with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * cascading resonance field
     */
    value: i32,
}

/**
 * Enum with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * enumerated variant collection
 */
pub enum Status {
    /**
     * Variant doc with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * active processing node
     */
    Active,

    /**
     * Another variant with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * suspended animation chamber
     */
    Idle {
        /**
         * Field in variant with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         * temporal duration metric
         */
        duration: u64,
    },

    /**
     * Tuple variant with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * error state container
     */
    Error(
        /**
         * Tuple field with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         * diagnostic error code
         */
        i32
    ),
}

/**
 * Union with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * memory-aligned data union
 */
pub union FloatOrInt {
    /**
     * Union field with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * floating-point representation
     */
    f: f32,

    /**
     * Another union field with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * integer bit pattern
     */
    i: i32,
}

/**
 * Trait definition with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * behavioral interface contract
 */
pub trait Processor {
    /**
     * Associated type with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * output data type
     */
    type Output;

    /**
     * Associated const with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * maximum buffer capacity
     */
    const MAX_SIZE: usize;

    /**
     * Trait method with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * processing operation handler
     */
    fn process(&self, input: &str) -> Self::Output;

    /**
     * Default method with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * validation check routine
     */
    fn validate(&self) -> bool {
        true
    }
}

/**
 * Trait alias with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * combined trait bounds
 */
pub trait ProcessorClone = Processor + Clone;

/**
 * Implementation block with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * trait implementation container
 */
impl Processor for Container {
    /**
     * Impl associated type with
     * @relation(REQ-OUTER-BLOCK-DOC)
     * Words: concrete output type
     */
    type Output = String;

    /**
     * Impl const with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * size constant value
     */
    const MAX_SIZE: usize = 1024;

    /**
     * Impl method with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * implementation of a process
     */
    fn process(&self, input: &str) -> Self::Output {
        format!("{}: {}", self.name, input)
    }
}

/**
 * Inherent impl with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * inherent method block
 */
impl Container {
    /**
     * Inherent method with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * constructor function pattern
     */
    pub fn new(name: String) -> Self {
        Self { name, value: 0 }
    }

    /**
     * Another method with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * getter accessor method
     */
    pub fn get_value(&self) -> i32 {
        self.value
    }
}

/**
 * Function with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * top-level function utility
 */
pub fn process_data(input: &str) -> String {
    input.to_uppercase()
}

/**
 * Async function with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * asynchronous operation handler
 */
pub async fn async_process(data: Vec<u8>) -> Result<(), std::io::Error> {
    Ok(())
}

/**
 * Const function with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * compile-time evaluable function
 */
pub const fn compute_magic(x: u32) -> u32 {
    x * 42
}

/**
 * Unsafe function with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * unchecked operation wrapper
 */
pub unsafe fn dangerous_operation(ptr: *mut u8) {
    if !ptr.is_null() {
        *ptr = 0;
    }
}

/**
 * External crate import with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * external dependency reference
 */
extern crate std;

/**
 * Module with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * nested module container
 */
pub mod submodule {
    //! Inner module doc with random docs:
    //! @relation(REQ-OUTER-LINE-DOC)
    //! module-level documentation

    /**
     * Nested struct with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * encapsulated data structure
     */
    pub struct Inner {
        /**
         * Field with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         * internal state variable
         */
        data: Vec<u8>,
    }
}

/**
 * Foreign function interface with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * external C interface block
 */
extern "C" {
    /**
     * Foreign function with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * C library function binding
     */
    fn external_func(x: i32) -> i32;

    /**
     * Foreign static with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * global C variable reference
     */
    static EXTERNAL_VAR: i32;

    /**
     * Foreign type with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * C type declaration
     */
    type OpaqueType;
}

/**
 * Macro invocation with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * declarative macro call
 */
macro_rules! test_macro {
    () => {
        println!("test");
    };
}

/**
 * Function with match arms containing doc attributes
 * This function demonstrates
 * @relation(REQ-OUTER-BLOCK-DOC)
 */
pub fn match_example(x: Option<i32>) -> i32 {
    match x {
        /**
         * Match arm with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         * some variant pattern
         */
        Some(val) => val,

        /**
         * None arm with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         * default fallback case
         */
        None => 0,
    }
}

/**
 * Generic function with random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * parameterized function template
 */
pub fn generic_fn<
    /**
     * Type parameter with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * generic type variable
     */
    T: Clone,

    /**
     * Const parameter with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * compile-time constant value
     */
    const N: usize,
>(
    input: [T; N],
) -> Vec<T> {
    input.to_vec()
}

/**
 * Struct with generic parameters random docs:
 * @relation(REQ-OUTER-BLOCK-DOC)
 * generic container structure
 */
pub struct GenericContainer<
    /**
     * Lifetime param with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * reference lifetime bound
     */
    'a,

    /**
     * Generic type param with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * primary type parameter
     */
    T,
> where
    T: 'a,
{
    /**
     * Reference field with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * borrowed data reference
     */
    pub data: &'a T,
}

/**
 * Test struct for field value attributes in expressions
 */
#[cfg(any(target_os = "linux", target_os = "macos"))]
/**
 * This demonstrates
 * @relation(REQ-OUTER-BLOCK-DOC)
 */
pub fn struct_expression_test() {
    let _ = Container {
        /**
         * Field value with random docs:
         * @relation(REQ-OUTER-BLOCK-DOC)
         */
        name: String::from("test"),
        value: 42,
    };
}

/**
 * Test if we can add a docstring to an expression literal
 */
fn expr_lit(x: i32) -> i32 {
    /**
     * Test an expression
     * @relation(REQ-OUTER-BLOCK-DOC)
     */
    8675309;
    /**
     * SURPRISING: We are documenting
     * @relation(REQ-OUTER-BLOCK-DOC)
     * the first part of the expression, not the entire expression,
     * see `test_not_surprising` for how to fix this
     */
    x + 2
}

fn test_not_surprising(x: i32) -> i32 {
    /**
     * Test documenting the
     * @relation(REQ-OUTER-BLOCK-DOC)
     */
    (x + 2)
}

#[cfg(any(test, doc))]
mod tests {
    /**
     * Test function with random docs:
     * @relation(REQ-OUTER-BLOCK-DOC)
     * unit test case definition
     */
    #[cfg_attr(not(doc), test)]
    fn test_basic() {
        assert_eq!(2 + 2, 4);
    }
}
