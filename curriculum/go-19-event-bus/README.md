# Event room

Build a synchronous event bus that permits subscriptions to change during delivery.

## Your brief

- Implement NewBus() *Bus, (*Bus).Subscribe(topic string,fn func(string)) func(), and (*Bus).Publish(topic,message string).
- Subscribe registers a callback and returns an idempotent unsubscribe function. A nil callback registers nothing and returns a callable no-op. Empty topics and messages are valid.
- Publish synchronously calls each subscription present at the start of that publish exactly once, in subscription order, only for the matching topic.
- Subscriptions added or removed during callbacks affect later publishes, not the current delivery snapshot. Callbacks may subscribe, unsubscribe or publish without deadlock.
- Bus operations are safe concurrently. Different simultaneous Publish calls may invoke the same callback concurrently; callbacks are responsible for their own shared data. Different buses are independent.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Synchronization](https://pkg.go.dev/sync)
- [Function types](https://pkg.go.dev/builtin)
