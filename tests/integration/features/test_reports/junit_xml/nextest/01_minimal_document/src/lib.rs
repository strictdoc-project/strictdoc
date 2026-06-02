pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    /// @relation(REQ-1, scope=function)
    #[test]
    fn add_works() {
        assert_eq!(add(2, 3), 5);
    }
}
