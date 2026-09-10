# Retry desk

Control a retryable operation without hiding its errors or ignoring cancellation.

## Your brief

- Implement Retry(ctx context.Context, attempts int, operation func() error) error.
- attempts is the maximum total number of calls and must be positive. A nil operation is invalid. Invalid arguments return an error without calling the operation.
- Check ctx.Err() before every call. Return that context error immediately when canceled; a pre-canceled context makes zero calls.
- Stop and return nil at the first successful call. If every allowed call fails, return the last operation error unchanged so errors.Is works.
- No delay or background goroutines are required. An operation that cancels the context and fails prevents the next attempt; a successful operation still returns nil.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Context](https://pkg.go.dev/context)
- [Errors](https://pkg.go.dev/errors)
