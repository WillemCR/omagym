package challenge

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestExpiry(t *testing.T) {
	c, e := New(time.Minute)
	if e != nil || c == nil {
		t.Fatal(e)
	}
	now := time.Unix(100, 0)
	c.Set("a", "note", now)
	if v, ok := c.Get("a", now.Add(time.Minute-time.Nanosecond)); !ok || v != "note" {
		t.Fatal(v, ok)
	}
	if v, ok := c.Get("a", now.Add(time.Minute)); ok || v != "" {
		t.Fatal("expiry boundary", v, ok)
	}
}
func TestReplacementAndIsolation(t *testing.T) {
	a, _ := New(time.Second)
	b, _ := New(time.Second)
	now := time.Unix(0, 0)
	a.Set("", "", now)
	if v, ok := a.Get("", now); !ok || v != "" {
		t.Fatal("empty value must exist")
	}
	a.Set("x", "old", now)
	a.Set("x", "new", now.Add(time.Second))
	if v, ok := a.Get("x", now.Add(1500*time.Millisecond)); !ok || v != "new" {
		t.Fatal(v, ok)
	}
	if _, ok := b.Get("x", now); ok {
		t.Fatal("shared caches")
	}
}
func TestInvalidTTL(t *testing.T) {
	for _, d := range []time.Duration{0, -1} {
		c, e := New(d)
		if e == nil || c != nil {
			t.Fatal("invalid TTL", c, e)
		}
	}
}
func TestConcurrentCache(t *testing.T) {
	c, _ := New(time.Hour)
	var wg sync.WaitGroup
	now := time.Unix(0, 0)
	for i := 0; i < 32; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			k := fmt.Sprint(i)
			for j := 0; j < 30; j++ {
				c.Set(k, k, now)
				if v, ok := c.Get(k, now); !ok || v != k {
					t.Errorf("lost %s", k)
				}
			}
		}(i)
	}
	wg.Wait()
}
