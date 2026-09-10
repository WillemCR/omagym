# Pocket API

Build a tiny, in-memory key/value service with a clean HTTP contract.

- Implement NewHandler() http.Handler in package keyserver. Each handler has its own empty store.
- PUT /kv/{key} stores the raw request body and responds 204. GET returns the stored body and 200, or 404 if missing.
- DELETE removes an existing key and responds 204; missing keys return 404. Other methods on valid paths return 405.
- Only paths with exactly one nonempty key segment after /kv/ are valid; other paths return 404.
- The handler must safely support simultaneous requests. Tests use in-process requests, without exposing a port.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
