# Recent activity

Keep a bounded history of recent events with a reusable generic ring buffer.

## Your brief

- Implement `New[T any](capacity int) (*Ring[T],error)`, `Push(value T) (T,bool)`, `Pop() (T,bool)`, and `Len() int` on `Ring[T]`.
- Capacity must be positive. Push appends a new newest item; when full it evicts and returns the oldest item with true. Otherwise return the zero value of T,false.
- Pop removes and returns the oldest item with true; an empty ring returns the zero value,false. Len reports the current number of items.
- Support arbitrary element types and repeated wraparound. Separate rings must not share state. Concurrent access is not required.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Generics tutorial](https://go.dev/doc/tutorial/generics)
- [Builtin functions](https://pkg.go.dev/builtin)
