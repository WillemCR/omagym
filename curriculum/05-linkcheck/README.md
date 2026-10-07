# Link patrol

Check a batch of URLs with bounded parallelism and cancellation.

- Implement Check(ctx context.Context, urls []string, workers int, probe Probe) ([]Result, error) in package linkcheck.
- Probe is func(context.Context, string) (int, error). Call it once per URL (unless canceled) using at most workers concurrent calls; workers must be positive.
- Return one Result per URL in the original input order, including duplicates. Result.Status and Result.Err hold exactly what the probe returned; keep processing other URLs after probe errors.
- Use parallelism when workers > 1. Assume probe honors its context. Leave no goroutines running after Check returns.
- Check ctx before starting each probe and again before returning. Once it is canceled, start no more probes and return nil results with the context's error, even for empty input.
- With a live context, empty input returns an empty result slice without error for valid workers. Tests inject probes; no internet access is needed.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
