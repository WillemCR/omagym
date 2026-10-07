package challenge

import (
	"math"
	"reflect"
	"sync"
	"sync/atomic"
	"testing"
)

func TestBatchTransfers(t *testing.T) {
	l, e := NewLedger(map[string]int64{"a": 100, "b": 0, "c": 0})
	if e != nil {
		t.Fatal(e)
	}
	e = l.Apply([]Transfer{{"a", "b", 70}, {"b", "c", 50}})
	if e != nil || !reflect.DeepEqual(l.Snapshot(), map[string]int64{"a": 30, "b": 20, "c": 50}) {
		t.Fatal(l.Snapshot(), e)
	}
	if e = l.Apply(nil); e != nil {
		t.Fatal(e)
	}
	l, _ = NewLedger(map[string]int64{"a": 100, "b": 0, "near": math.MaxInt64 - 1})
	if e = l.Apply([]Transfer{{"a", "b", 100}, {"b", "near", 1}}); e != nil || !reflect.DeepEqual(l.Snapshot(), map[string]int64{"a": 0, "b": 99, "near": math.MaxInt64}) {
		t.Fatal("exact-balance or boundary transfer rejected", l.Snapshot(), e)
	}
}
func TestRollbackAndValidation(t *testing.T) {
	initial := map[string]int64{"a": 100, "b": 0, "rich": math.MaxInt64, "near": math.MaxInt64 - 1}
	for _, bad := range []Transfer{{"b", "a", 200}, {"b", "a", 6}, {"missing", "a", 1}, {"a", "missing", 1}, {"a", "a", 1}, {"a", "b", 0}, {"a", "b", -1}, {"a", "rich", 1}, {"a", "near", 2}} {
		l, _ := NewLedger(initial)
		e := l.Apply([]Transfer{{"a", "b", 5}, bad})
		if e == nil || !reflect.DeepEqual(l.Snapshot(), initial) {
			t.Error(bad, l.Snapshot(), e)
		}
	}
	start := map[string]int64{"a": 100, "b": 0, "c": 0}
	l, _ := NewLedger(start)
	if e := l.Apply([]Transfer{{"a", "b", 30}, {"b", "c", 10}, {"c", "missing", 1}}); e == nil || !reflect.DeepEqual(l.Snapshot(), start) {
		t.Error("rollback after reusing an account", l.Snapshot(), e)
	}
}
func TestLedgerCopies(t *testing.T) {
	m := map[string]int64{"a": 10}
	l, _ := NewLedger(m)
	m["a"] = 99
	s := l.Snapshot()
	if s["a"] != 10 {
		t.Fatal(s)
	}
	s["a"] = 88
	if l.Snapshot()["a"] != 10 {
		t.Fatal("snapshot aliases")
	}
	for _, bad := range []map[string]int64{{"": 0}, {"a": -1}} {
		l, e := NewLedger(bad)
		if e == nil || l != nil {
			t.Fatal(l, e)
		}
	}
	l, e := NewLedger(nil)
	if e != nil || len(l.Snapshot()) != 0 {
		t.Fatal(l, e)
	}
	first, _ := NewLedger(map[string]int64{"alice": 100, "carol": 0})
	second, _ := NewLedger(map[string]int64{"bob": 200, "dave": 0})
	if e := first.Apply([]Transfer{{"alice", "carol", 40}}); e != nil {
		t.Fatal(e)
	}
	if e := second.Apply([]Transfer{{"bob", "dave", 70}}); e != nil {
		t.Fatal(e)
	}
	if !reflect.DeepEqual(first.Snapshot(), map[string]int64{"alice": 60, "carol": 40}) || !reflect.DeepEqual(second.Snapshot(), map[string]int64{"bob": 130, "dave": 70}) {
		t.Fatal("ledgers share state", first.Snapshot(), second.Snapshot())
	}
}
func TestConcurrentLedger(t *testing.T) {
	l, _ := NewLedger(map[string]int64{"a": 10000, "b": 0, "c": 0})
	var wg sync.WaitGroup
	var report sync.Once
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 50; j++ {
				e := l.Apply([]Transfer{{"a", "b", 2}, {"b", "c", 1}})
				s := l.Snapshot()
				if e != nil || s["b"] != s["c"] || s["a"]+s["b"]+s["c"] != 10000 {
					report.Do(func() { t.Error("failed or observed partial batch", s, e) })
				}
			}
		}()
	}
	wg.Wait()
	if s := l.Snapshot(); !reflect.DeepEqual(s, map[string]int64{"a": 8000, "b": 1000, "c": 1000}) {
		t.Fatal("lost or duplicated concurrent transfers", s)
	}
	// Many transfers compete for a balance that can pay exactly one of them.
	for round := 0; round < 200; round++ {
		l, _ := NewLedger(map[string]int64{"a": 1, "b": 0})
		start := make(chan struct{})
		var ok atomic.Int64
		for i := 0; i < 8; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				<-start
				if l.Apply([]Transfer{{"a", "b", 1}}) == nil {
					ok.Add(1)
				}
			}()
		}
		close(start)
		wg.Wait()
		if s := l.Snapshot(); ok.Load() != 1 || s["a"] != 0 || s["b"] != 1 {
			t.Fatal("competing transfers overspent or all failed", ok.Load(), s)
		}
	}
}
