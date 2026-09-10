# Expiring notes

Build an expiring string cache with an explicit clock so its behavior is deterministic.

## Your brief

- Implement New(ttl time.Duration) (*Cache,error), (*Cache).Set(key,value string, now time.Time), and (*Cache).Get(key string, now time.Time) (string,bool).
- New requires a positive TTL. Each Set stores a value until now+ttl and replaces any existing value and expiry for that key.
- Get succeeds only before the expiry instant. At or after expiry it returns empty string,false. A missing key does the same; empty keys and values are allowed.
- Different caches are independent. Set and Get must be safe for concurrent use. Tests pass explicit times; do not sleep or consult the wall clock.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Time](https://pkg.go.dev/time)
- [Synchronization](https://pkg.go.dev/sync)
