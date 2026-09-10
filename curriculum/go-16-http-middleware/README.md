# Private endpoint

Protect an existing HTTP handler with a small bearer-token middleware.

## Your brief

- Implement RequireToken(next http.Handler,token string) http.Handler. The returned handler only calls next when Authorization equals exactly Bearer followed by one space and token.
- An empty configured token always denies access. Missing, incorrect or differently formatted Authorization returns status 401, header WWW-Authenticate: Bearer, and body unauthorized followed by a newline.
- Successful requests preserve next's status, headers and body and pass through the original request including method, URL and body. Do not alter it.
- Support simultaneous requests with no shared request state. Tests run handlers in process; no listening port is needed.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [HTTP handlers](https://pkg.go.dev/net/http)
- [HTTP testing](https://pkg.go.dev/net/http/httptest)
