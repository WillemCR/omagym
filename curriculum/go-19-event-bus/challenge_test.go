package challenge

import (
	"reflect"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestTopicDelivery(t *testing.T) {
	b := NewBus()
	got := []string{}
	stop := b.Subscribe("a", func(s string) { got = append(got, "1:"+s) })
	b.Subscribe("a", func(s string) { got = append(got, "2:"+s) })
	b.Subscribe("b", func(s string) { t.Error("wrong topic") })
	b.Publish("a", "hi")
	stop()
	stop()
	b.Publish("a", "bye")
	want := []string{"1:hi", "2:hi", "2:bye"}
	if !reflect.DeepEqual(got, want) {
		t.Fatal(got)
	}
	func() {
		defer func() {
			if r := recover(); r != nil {
				t.Fatal("nil callback was registered:", r)
			}
		}()
		stopNil := b.Subscribe("a", nil)
		b.Publish("a", "nil")
		stopNil()
		stopNil()
	}()
	want = append(want, "2:nil")
	dup := 0
	count := func(string) { dup++ }
	stopFirst := b.Subscribe("dup", count)
	b.Subscribe("dup", count)
	stopFirst()
	b.Publish("dup", "")
	if dup != 1 {
		t.Fatal("unsubscribe removed another registration of the same callback", dup)
	}
	NewBus().Publish("a", "other")
	if !reflect.DeepEqual(got, want) {
		t.Fatal("different buses share subscriptions", got)
	}
}
func TestDeliverySnapshot(t *testing.T) {
	b := NewBus()
	got := []string{}
	var stopSecond func()
	added := false
	b.Subscribe("x", func(string) {
		got = append(got, "first")
		stopSecond()
		if !added {
			added = true
			b.Subscribe("x", func(string) { got = append(got, "third") })
		}
	})
	stopSecond = b.Subscribe("x", func(string) { got = append(got, "second") })
	b.Publish("x", "")
	b.Publish("x", "")
	if !reflect.DeepEqual(got, []string{"first", "second", "first", "third"}) {
		t.Fatal(got)
	}
}
func TestReentrantPublish(t *testing.T) {
	b := NewBus()
	n := 0
	got := []string{}
	b.Subscribe("outer", func(string) { b.Publish("inner", "x") })
	b.Subscribe("inner", func(string) { n++ })
	b.Subscribe("loop", func(m string) {
		got = append(got, m)
		if m == "first" {
			b.Publish("loop", "nested")
			got = append(got, "returned")
		}
	})
	done := make(chan struct{})
	go func() {
		defer close(done)
		b.Publish("outer", "")
		b.Publish("loop", "first")
	}()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("publishing from a callback deadlocked")
	}
	if n != 1 || !reflect.DeepEqual(got, []string{"first", "nested", "returned"}) {
		t.Fatal(n, got)
	}
}
func TestConcurrentBus(t *testing.T) {
	b := NewBus()
	var n atomic.Int64
	b.Subscribe("", func(string) { n.Add(1) })
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 20; j++ {
				stop := b.Subscribe("unused", func(string) {})
				b.Publish("", "")
				stop()
			}
		}()
	}
	var late atomic.Int64
	stop := b.Subscribe("shared", func(string) { late.Add(1) })
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			stop()
		}()
	}
	wg.Wait()
	b.Publish("shared", "")
	if n.Load() != 400 || late.Load() != 0 {
		t.Fatal(n.Load(), late.Load())
	}
}
