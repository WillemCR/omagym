# Tiny config reader

Parse a human-edited service configuration and point to the first broken line.

- Implement parse_config(text: &str) -> Result<BTreeMap<String, String>, ConfigError>. ConfigError has line: usize and kind: ErrorKind (InvalidLine, InvalidKey, DuplicateKey).
- Use 1-based physical line numbers. Trim each line; ignore blank lines and lines whose trimmed text starts with #. Inline # is ordinary value text.
- Each remaining line must contain =. Split at its first =, then trim key and value. Empty values are valid and later = characters stay in the value.
- Keys are case-sensitive and must begin with an ASCII letter or underscore; remaining characters may be ASCII letters, digits or underscores.
- Reject the first bad line: missing = is InvalidLine, a malformed key is InvalidKey, and a previously seen valid key is DuplicateKey. Return no partial map.

Start in `src/lib.rs`. Keep public signatures and types. The starter deliberately has no implementation.

Run `cargo test --offline` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [Result](https://doc.rust-lang.org/std/result/enum.Result.html)
- [String slices](https://doc.rust-lang.org/std/primitive.str.html)
- [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html)
