package linkcheck

import "context"

type Probe func(context.Context, string) (int, error)
type Result struct {
	URL    string
	Status int
	Err    error
}

func Check(ctx context.Context, urls []string, workers int, probe Probe) ([]Result, error) {
	return nil, nil
}
