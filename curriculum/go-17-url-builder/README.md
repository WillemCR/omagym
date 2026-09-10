# Search links

Generate shareable search links without losing existing URL details.

## Your brief

- Implement AddQuery(base string,params map[string][]string) (string,error).
- Accept absolute http or https URLs with a nonempty hostname and no user information. Reject malformed URLs, invalid percent escapes and malformed existing query strings.
- Preserve the path, fragment, and existing query keys not present in params. For each supplied key, replace all old values with the given values in their original order; a nil or empty slice deletes that key.
- Encode the resulting query using Go url.Values.Encode semantics, including lexicographically sorted keys and escaped special characters.
- Do not mutate params or its slices. Invalid input returns empty string and an error.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [URL parsing](https://pkg.go.dev/net/url)
