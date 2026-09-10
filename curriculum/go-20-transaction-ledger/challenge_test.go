package challenge

import (
	"math"
	"reflect"
	"sync"
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
}
func TestRollbackAndValidation(t *testing.T) {
	initial := map[string]int64{"a": 100, "b": 0, "rich": math.MaxInt64}
	for _, bad := range []Transfer{{"b", "a", 200}, {"missing", "a", 1}, {"a", "missing", 1}, {"a", "a", 1}, {"a", "b", 0}, {"a", "b", -1}, {"a", "rich", 1}} {
		l, _ := NewLedger(initial)
		e := l.Apply([]Transfer{{"a", "b", 5}, bad})
		if e == nil || !reflect.DeepEqual(l.Snapshot(), initial) {
			t.Error(bad, l.Snapshot(), e)
		}
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
}
func TestConcurrentLedger(t *testing.T) {
	l, _ := NewLedger(map[string]int64{"a": 10000, "b": 10000})
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 30; j++ {
				if e := l.Apply([]Transfer{{"a", "b", 1}, {"b", "a", 1}}); e != nil {
					t.Error(e)
				}
				s := l.Snapshot()
				if s["a"] != 10000 || s["b"] != 10000 {
					t.Error("observed partial batch", s)
				}
			}
		}()
	}
	wg.Wait()
	if s := l.Snapshot(); s["a"] != 10000 || s["b"] != 10000 {
		t.Fatal(s)
	}
}
