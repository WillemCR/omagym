# Launch config

Turn a small configuration file into a validated server configuration.

## Your brief

- Implement Parse(text string) (Config, error) in package challenge. Config has Address string, Workers int, Debug bool.
- Start with Address=127.0.0.1:8080, Workers=4, Debug=false. Ignore blank lines and lines whose trimmed form begins with #.
- Other lines are key=value; trim whitespace around both sides. Supported keys are address, workers, debug. Each key may appear only once.
- address must be nonempty; workers must be a base-10 integer from 1 through 64; debug must be exactly true or false.
- Reject missing =, unknown keys, duplicates and invalid values. On any error return Config{}; values may contain additional = characters.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Strings](https://pkg.go.dev/strings)
- [Integer parsing](https://pkg.go.dev/strconv)
