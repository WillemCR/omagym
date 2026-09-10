package challenge

import "testing"

func TestEvictionOrder(t *testing.T) {
	r, e := New[int](2)
	if e != nil || r == nil {
		t.Fatal(e)
	}
	if v, ok := r.Push(10); v != 0 || ok {
		t.Fatal(v, ok)
	}
	r.Push(20)
	if v, ok := r.Push(30); v != 10 || !ok {
		t.Fatal(v, ok)
	}
	if r.Len() != 2 {
		t.Fatal(r.Len())
	}
	for _, want := range []int{20, 30} {
		if v, ok := r.Pop(); v != want || !ok {
			t.Fatal(v, ok)
		}
	}
	if v, ok := r.Pop(); v != 0 || ok || r.Len() != 0 {
		t.Fatal(v, ok)
	}
}
func TestWrapAndTypes(t *testing.T) {
	type event struct{ Name string }
	r, _ := New[event](1)
	for i := 0; i < 100; i++ {
		r.Push(event{"hello"})
		if v, ok := r.Pop(); !ok || v.Name != "hello" {
			t.Fatal(v, ok)
		}
	}
	a, _ := New[string](1)
	b, _ := New[string](1)
	a.Push("a")
	if _, ok := b.Pop(); ok {
		t.Fatal("shared storage")
	}
}
func TestInvalidCapacity(t *testing.T) {
	for _, n := range []int{0, -3} {
		r, e := New[int](n)
		if e == nil || r != nil {
			t.Fatal("accepted capacity", n)
		}
	}
}
