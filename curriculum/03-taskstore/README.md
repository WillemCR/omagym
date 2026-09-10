# Task notebook

Create a small task store that survives a restart.

- Implement Save(path string, tasks []Task) error and Load(path string) ([]Task, error) in package taskstore.
- Task has ID int, Title string, Done bool, with JSON keys id, title, done. Save writes a JSON array, preserving input order and values.
- Both Save and Load reject IDs <= 0, duplicate IDs, and whitespace-only titles. Return an error before writing invalid tasks.
- Load returns an empty slice without error when the file does not exist. Reject malformed JSON and trailing JSON values; propagate other I/O errors.
- Save(nil) writes an empty JSON array. You need not create missing parent directories.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
