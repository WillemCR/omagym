# Sensor report

Turn noisy sensor readings into a compact, predictable report.

- Implement summarize(readings: &[i32]) -> Option<Report>. Return None for an empty slice.
- Report contains count: usize, min: i32, max: i32, total: i64 and rising: usize.
- Count every reading and sum using i64 so multiple large i32 values cannot overflow.
- rising counts adjacent pairs where the second reading is strictly greater than the first. Equal readings do not count. Do not change the input.

Start in `src/lib.rs`. Keep public signatures and types. The starter deliberately has no implementation.

Run `cargo test --offline` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [Slices](https://doc.rust-lang.org/std/primitive.slice.html)
- [Option](https://doc.rust-lang.org/std/option/enum.Option.html)
