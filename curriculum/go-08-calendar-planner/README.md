# Busy blocks

Combine overlapping calendar bookings into a clean list of busy periods.

## Your brief

- Implement Merge(input []Interval) ([]Interval, error) in package challenge. Interval has Start and End int, measured in minutes.
- Each interval must satisfy 0 <= Start < End <= 1440. Invalid input returns nil and an error.
- Return intervals sorted by Start, combining overlaps and touching endpoints. A booking ending at 60 and one starting at 60 form one block.
- Do not mutate or alias the input slice. Empty input succeeds with an empty result; nil and empty results are both acceptable.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Sorting](https://pkg.go.dev/sort)
- [Slices](https://pkg.go.dev/slices)
