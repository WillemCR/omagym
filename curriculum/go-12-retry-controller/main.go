package challenge

import "context"

func Retry(ctx context.Context, attempts int, operation func() error) error { return nil }
