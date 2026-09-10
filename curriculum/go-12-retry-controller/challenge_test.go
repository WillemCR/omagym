package challenge

import (
	"context"
	"errors"
	"testing"
)

func TestRetrySuccess(t *testing.T) {
	n := 0
	e := Retry(context.Background(), 5, func() error {
		n++
		if n < 3 {
			return errors.New("temporary")
		}
		return nil
	})
	if e != nil || n != 3 {
		t.Fatal(n, e)
	}
}
func TestFinalError(t *testing.T) {
	last := errors.New("last")
	n := 0
	e := Retry(context.Background(), 3, func() error { n++; return last })
	if !errors.Is(e, last) || n != 3 {
		t.Fatal(n, e)
	}
}
func TestCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	n := 0
	e := Retry(ctx, 3, func() error { n++; return nil })
	if !errors.Is(e, context.Canceled) || n != 0 {
		t.Fatal(n, e)
	}
	ctx, cancel = context.WithCancel(context.Background())
	e = Retry(ctx, 4, func() error { n++; cancel(); return errors.New("retry") })
	if n != 1 || !errors.Is(e, context.Canceled) {
		t.Fatal(n, e)
	}
	ctx, cancel = context.WithCancel(context.Background())
	e = Retry(ctx, 2, func() error { cancel(); return nil })
	if e != nil {
		t.Fatal(e)
	}
}
func TestInvalidRetry(t *testing.T) {
	n := 0
	for _, a := range []int{0, -1} {
		if e := Retry(context.Background(), a, func() error { n++; return nil }); e == nil {
			t.Fatal("accepted attempts")
		}
	}
	if e := Retry(context.Background(), 1, nil); e == nil || n != 0 {
		t.Fatal(n, e)
	}
}
