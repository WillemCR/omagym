package challenge

import (
	"reflect"
	"sync"
	"sync/atomic"
	"testing"
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
	b.Subscribe("a", nil)()
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
	b.Subscribe("outer", func(string) { b.Publish("inner", "x") })
	b.Subscribe("inner", func(string) { n++ })
	b.Publish("outer", "")
	if n != 1 {
		t.Fatal(n)
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
	wg.Wait()
	if n.Load() != 400 {
		t.Fatal(n.Load())
	}
}
