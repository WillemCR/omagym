# Mail preview

Render a safe HTML email preview from a template and recipient data.

## Your brief

- Implement Render(source string,data map[string]string) (string,error) using Go HTML template semantics.
- Support ordinary field references such as {{.Name}}, conditionals, and standard built-in template functions. Escape inserted values according to their HTML context.
- A missing map key, invalid template syntax, or execution failure returns empty string and an error, never partial rendered output.
- An empty template succeeds with an empty string. Preserve ordinary source whitespace. Do not mutate data or treat values as trusted HTML.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [HTML templates](https://pkg.go.dev/html/template)
- [Bytes buffers](https://pkg.go.dev/bytes)
