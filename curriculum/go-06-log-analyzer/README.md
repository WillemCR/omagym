# Log desk

Summarize a stream of application log events without keeping the whole log in memory.

## Your brief

- Implement Analyze(r io.Reader) (Report, error) in package challenge. Report has Counts map[string]int and LastError string.
- Each nonblank line has LEVEL|message. Split at the first |, trim both parts, and allow INFO, WARN and ERROR only. Additional | characters belong to the message.
- Count each level and remember the last ERROR message. Empty messages, unknown levels or missing delimiters return a nil Counts map and an error.
- Ignore whitespace-only lines. Empty input succeeds with an empty map. Propagate reader errors; inputs have lines shorter than 32 KiB.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Buffered scanning](https://pkg.go.dev/bufio)
- [String operations](https://pkg.go.dev/strings)
- [Readers](https://pkg.go.dev/io)
