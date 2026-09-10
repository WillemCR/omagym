# Link patrol

Check a batch of URLs with bounded parallelism and cancellation.

- Implement Check(ctx context.Context, urls []string, workers int, probe Probe) ([]Result, error) in package linkcheck.
- Probe is func(context.Context, string) (int, error). Call it once per URL using at most workers concurrent calls; workers must be positive.
- Return one Result per URL in the original input order, including duplicates. Record probe errors in Result.Err and keep processing other URLs.
- Use parallelism when workers > 1. Propagate context cancellation as the top-level error. Assume probe honors its context.
- Empty input returns an empty result slice without error for valid workers. Tests inject probes; no internet access is needed.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
