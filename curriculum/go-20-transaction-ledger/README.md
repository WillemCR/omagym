# Atomic wallet

Apply batches of wallet transfers atomically while keeping account balances consistent.

## Your brief

- Implement NewLedger(initial map[string]int64) (*Ledger,error), (*Ledger).Apply(batch []Transfer) error, and (*Ledger).Snapshot() map[string]int64. Transfer has From,To string and Cents int64.
- NewLedger rejects empty account names and negative balances, and copies the input map. Nil input creates an empty ledger.
- Apply validates and applies transfers in order against tentative balances. Both accounts must exist, From must differ from To, Cents must be positive, the sender must have enough funds and the recipient balance must not overflow int64.
- If any transfer fails, roll back the whole batch. Empty batches succeed. Later transfers may spend funds received earlier in the same batch.
- Snapshot returns an independent copy. All methods must be safe concurrently and each Apply batch must be atomic relative to other operations.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Synchronization](https://pkg.go.dev/sync)
- [Integer limits](https://pkg.go.dev/math)
- [Errors](https://pkg.go.dev/errors)
