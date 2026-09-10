package linkcheck

import (
	"context"
	"errors"
	"sync/atomic"
	"testing"
	"time"
)

func TestOrderAndErrors(t *testing.T) {
	bad := errors.New("offline")
	urls := []string{"slow", "bad", "fast", "fast"}
	var calls atomic.Int32
	got, err := Check(context.Background(), urls, 3, func(ctx context.Context, u string) (int, error) {
		calls.Add(1)
		if u == "slow" {
			time.Sleep(20 * time.Millisecond)
		}
		if u == "bad" {
			return 0, bad
		}
		return 200, nil
	})
	if err != nil || len(got) != len(urls) {
		t.Fatalf("got %v %v; want 4 results", got, err)
	}
	for i, u := range urls {
		if got[i].URL != u {
			t.Errorf("result %d out of order", i)
		}
		if u == "bad" && !errors.Is(got[i].Err, bad) {
			t.Error("probe error lost")
		}
		if u != "bad" && (got[i].Status != 200 || got[i].Err != nil) {
			t.Error("success result incorrect")
		}
	}
	if calls.Load() != 4 {
		t.Error("probe should run once per URL including duplicates")
	}
}
func TestParallelAndBounded(t *testing.T) {
	var active, peak atomic.Int32
	started := make(chan struct{}, 10)
	release := make(chan struct{})
	done := make(chan struct{})
	go func() {
		defer close(done)
		Check(context.Background(), []string{"a", "b", "c", "d", "e"}, 2, func(ctx context.Context, u string) (int, error) {
			n := active.Add(1)
			for p := peak.Load(); n > p && !peak.CompareAndSwap(p, n); p = peak.Load() {
			}
			started <- struct{}{}
			<-release
			active.Add(-1)
			return 200, nil
		})
	}()
	defer close(release)
	for i := 0; i < 2; i++ {
		select {
		case <-started:
		case <-done:
			t.Fatal("returned without checking URLs")
		case <-time.After(time.Second):
			t.Fatal("two probes should start concurrently")
		}
	}
	if peak.Load() > 2 {
		t.Error("worker limit exceeded")
	}
	release <- struct{}{}
	release <- struct{}{}
	release <- struct{}{}
	release <- struct{}{}
	release <- struct{}{}
	<-done
	if peak.Load() > 2 {
		t.Error("worker limit exceeded")
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
	_, err := Check(ctx, []string{"x"}, 1, func(ctx context.Context, u string) (int, error) { return 0, ctx.Err() })
	if !errors.Is(err, context.Canceled) {
		t.Error("cancellation should be returned")
	}
}
func TestCancellationDuringWork(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	started := make(chan struct{})
	done := make(chan error, 1)
	go func() {
		_, err := Check(ctx, []string{"x", "y"}, 1, func(ctx context.Context, u string) (int, error) {
			select {
			case <-started:
			default:
				close(started)
			}
			<-ctx.Done()
			return 0, ctx.Err()
		})
		done <- err
	}()
	select {
	case <-started:
		cancel()
	case <-time.After(time.Second):
		t.Fatal("probe did not start")
	}
	select {
	case err := <-done:
		if !errors.Is(err, context.Canceled) {
			t.Error("lost cancellation")
		}
	case <-time.After(time.Second):
		t.Fatal("cancellation did not stop work")
	}
}
