# Atomic stock ledger

Apply a delivery or order batch without leaving half-finished stock changes.

- Implement apply_batch(stock: &mut BTreeMap<String, u32>, changes: &[Change]) -> Result<(), BatchError>. Change has sku: String and delta: i64. BatchError has index: usize and kind: ErrorKind (InvalidSku, Underflow, Overflow).
- Process changes in input order. A missing SKU starts at zero; deltas can add or remove units. Values must stay within 0..=u32::MAX after each individual change.
- A SKU is valid only when non-empty and has no leading or trailing whitespace. Preserve case and inner whitespace. Validate SKU before checking its amount.
- Return the first failure with its zero-based change index. Negative stock is Underflow; stock above u32::MAX is Overflow, including extreme i64 deltas without panicking.
- A failed batch must leave the original map exactly unchanged. On success commit all changes. Keep zero-valued entries, including a new SKU with delta zero. An empty batch succeeds unchanged.

Start in `src/lib.rs`. Keep public signatures and types. The starter deliberately has no implementation.

Run `cargo test --offline` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html)
- [Mutable references](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
- [Integer arithmetic](https://doc.rust-lang.org/std/primitive.i64.html)
