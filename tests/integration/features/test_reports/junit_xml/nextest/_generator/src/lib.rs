pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_works() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn fails_on_purpose() {
        assert_eq!(add(1, 1), 3);
    }

    mod nested {
        use super::*;

        #[test]
        fn nested_module_test() {
            assert_eq!(add(0, 0), 0);
        }
    }
}
