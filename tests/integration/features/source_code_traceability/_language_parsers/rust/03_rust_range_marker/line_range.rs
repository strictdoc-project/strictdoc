fn main() {
    // Make `optional` of type `Option<i32>`
    // @relation(REQ-LINE-RANGE, scope=line)
    let mut optional = Some(0);

    // This reads: "while `let` destructures `optional` into
    // `Some(i)`, evaluate the block (`{}`). Else `break`.
    // @relation(REQ-LINE-RANGE, scope=range_start)
    while let Some(i) = optional {
        if i > 9 {
            println!("Greater than 9, quit!");
            optional = None;
        } else {
            println!("`i` is `{:?}`. Try again.", i);
            optional = Some(i + 1);
        }
        // ^ Less rightward drift and doesn't require
        // explicitly handling the failing case.
    }
    // @relation(REQ-LINE-RANGE, scope=range_end)

    // ^ `if let` had additional optional `else`/`else if`
    // clauses. `while let` does not have these.

    // @relation(REQ-LINE-RANGE, scope=file)
}
