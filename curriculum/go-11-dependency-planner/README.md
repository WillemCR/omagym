# Build order

Plan a deterministic build order for a collection of dependent tasks.

## Your brief

- Implement Order(graph map[string][]string) ([]string,error). Each map key is a task; its values are prerequisite task names.
- Return each task exactly once after all its prerequisites. Whenever multiple unfinished tasks are ready, choose the lexicographically smallest next.
- Reject a prerequisite absent from the graph, any cycle (including self-dependencies), and empty task names. Return nil on error.
- Duplicate prerequisite entries count as one dependency. Do not mutate the graph or its slices. Empty graphs succeed with an empty result.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Maps](https://pkg.go.dev/maps)
- [Sorting](https://pkg.go.dev/sort)
