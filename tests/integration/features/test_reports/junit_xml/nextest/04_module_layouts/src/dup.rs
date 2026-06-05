#[cfg(test)]
mod tests {
    /// @relation(REQ-DUP-A, scope=function)
    #[test]
    fn dup_works() { assert_eq!(1, 1); }
}
