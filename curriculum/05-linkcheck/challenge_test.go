package linkcheck

import (
	"context"
	"errors"
	"runtime"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestOrderAndErrors(t *testing.T) {
	bad := errors.New("offline")
	urls := []string{"slow", "bad", "fast", "fast"}
	codes := map[string]int{"slow": 301, "bad": 503, "fast": 404}
	var calls atomic.Int32
	got, err := Check(context.Background(), urls, 3, func(ctx context.Context, u string) (int, error) {
		calls.Add(1)
		if u == "slow" {
			time.Sleep(20 * time.Millisecond)
		}
		if u == "bad" {
			return codes[u], bad
		}
		return codes[u], nil
	})
	if err != nil || len(got) != len(urls) {
		t.Fatalf("got %v %v; want 4 results", got, err)
	}
	for i, u := range urls {
		if got[i].URL != u {
			t.Errorf("result %d out of order", i)
		}
		if got[i].Status != codes[u] {
			t.Errorf("%s: status %d; want the probe's %d", u, got[i].Status, codes[u])
		}
		if u == "bad" && !errors.Is(got[i].Err, bad) {
			t.Error("probe error lost")
		}
		if u != "bad" && got[i].Err != nil {
			t.Error("success result incorrect")
		}
	}
	if calls.Load() != 4 {
		t.Error("probe should run once per URL including duplicates")
	}
}
func TestParallelAndBounded(t *testing.T) {
	var active, peak, calls atomic.Int32
	started := make(chan struct{}, 10)
	release := make(chan struct{})
	var once sync.Once
	free := func() { once.Do(func() { close(release) }) }
	t.Cleanup(free)
	done := make(chan struct{})
	go func() {
		defer close(done)
		Check(context.Background(), []string{"a", "b", "c", "d", "e"}, 2, func(ctx context.Context, u string) (int, error) {
			calls.Add(1)
			n := active.Add(1)
			for p := peak.Load(); n > p && !peak.CompareAndSwap(p, n); p = peak.Load() {
			}
			started <- struct{}{}
			<-release
			active.Add(-1)
			return 200, nil
		})
	}()
	for i := 0; i < 2; i++ {
		select {
		case <-started:
		case <-done:
			t.Fatal("returned without checking URLs")
		case <-time.After(5 * time.Second):
			t.Fatal("two probes should start concurrently")
		}
	}
	select {
	case <-started:
		t.Fatal("worker limit exceeded")
	case <-time.After(50 * time.Millisecond):
	}
	free()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("Check did not finish after probes returned")
	}
	if peak.Load() > 2 {
		t.Error("worker limit exceeded")
	}
	if calls.Load() != 5 {
		t.Errorf("probe ran %d times; want 5", calls.Load())
	}
}
func TestInvalidWorkers(t *testing.T) {
	for _, n := range []int{0, -1} {
		if _, err := Check(context.Background(), nil, n, nil); err == nil {
			t.Error("invalid worker count accepted")
		}
	}
}
func TestEmpty(t *testing.T) {
	got, err := Check(context.Background(), nil, 1, func(context.Context, string) (int, error) { t.Error("unexpected probe"); return 0, nil })
	if err != nil || len(got) != 0 {
		t.Error("empty input should succeed")
	}
}
func TestCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	for _, urls := range [][]string{nil, {"x"}} {
		got, err := Check(ctx, urls, 1, func(ctx context.Context, u string) (int, error) {
			t.Error("probe called after cancellation")
			return 0, ctx.Err()
		})
		if !errors.Is(err, context.Canceled) || got != nil {
			t.Errorf("canceled context: got %v, %v; want nil, context.Canceled", got, err)
		}
	}
	ctx, cancel = context.WithCancel(context.Background())
	got, err := Check(ctx, []string{"x"}, 1, func(context.Context, string) (int, error) {
		cancel()
		return 200, nil
	})
	if !errors.Is(err, context.Canceled) || got != nil {
		t.Errorf("canceled during last probe: got %v, %v; want nil, context.Canceled", got, err)
	}
}
func TestCancellationDuringWork(t *testing.T) {
	for round := 0; round < 3; round++ {
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		base := runtime.NumGoroutine()
		var starts atomic.Int32
		started := make(chan struct{}, 5)
		type outcome struct {
			res []Result
			err error
		}
		done := make(chan outcome, 1)
		go func() {
			res, err := Check(ctx, []string{"a", "b", "c", "d", "e"}, 4, func(ctx context.Context, u string) (int, error) {
				starts.Add(1)
				started <- struct{}{}
				<-ctx.Done()
				return 0, ctx.Err()
			})
			done <- outcome{res, err}
		}()
		select {
		case <-started:
		case <-time.After(5 * time.Second):
			t.Fatal("probe did not start")
		}
		time.Sleep(50 * time.Millisecond) // let other workers start too
		cancel()
		select {
		case o := <-done:
			if !errors.Is(o.err, context.Canceled) || o.res != nil {
				t.Fatalf("got %v, %v; want nil, context.Canceled", o.res, o.err)
			}
		case <-time.After(5 * time.Second):
			t.Fatal("cancellation did not stop work")
		}
		// Every probe blocks until cancellation, so each worker may start at most one.
		if n := starts.Load(); n > 4 {
			t.Fatalf("%d probes started; none may start after cancellation", n)
		}
		for deadline := time.Now().Add(5 * time.Second); runtime.NumGoroutine() > base; time.Sleep(10 * time.Millisecond) {
			if time.Now().After(deadline) {
				t.Fatalf("%d goroutines still running after Check returned", runtime.NumGoroutine()-base)
			}
		}
	}
}
