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
	q, _ := New[[]byte](3)
	var model []byte
	for i := 0; i < 30; i++ {
		for j := 0; j < 1+i%3; j++ {
			v, ok := q.Push([]byte{byte(10*i + j)})
			if full := len(model) == 3; ok != full || (full && v[0] != model[0]) {
				t.Fatal("push", i, j, v, ok, "model", model)
			}
			if len(model) == 3 {
				model = model[1:]
			}
			model = append(model, byte(10*i+j))
		}
		if v, ok := q.Pop(); !ok || v[0] != model[0] {
			t.Fatal("pop", v, ok, "model", model)
		}
		model = model[1:]
		if q.Len() != len(model) {
			t.Fatal("len", q.Len(), "want", len(model))
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
