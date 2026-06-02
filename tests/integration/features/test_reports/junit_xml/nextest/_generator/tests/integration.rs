use my_crate::add;

#[test]
fn integration_add() {
    assert_eq!(add(2, 2), 4);
}
