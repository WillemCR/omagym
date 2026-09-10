# Snapshot review

Show exactly what changed between two named configuration snapshots.

## Your brief

- Implement Diff(before,after map[string]string) []Change. Change has Key, Kind, Before, After string fields.
- Emit one Change for every added, removed or changed key, sorted lexicographically by Key. Kind is exactly added, removed or changed.
- For added keys Before is empty; for removed keys After is empty. An existing empty value differs from an absent key.
- Omit unchanged keys. Nil maps behave as empty maps. Do not mutate either input; empty output may be nil or an empty slice.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Sorting](https://pkg.go.dev/sort)
- [Maps](https://pkg.go.dev/maps)
