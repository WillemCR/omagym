package challenge

import (
	"reflect"
	"testing"
)

func TestChanges(t *testing.T) {
	a := map[string]string{"a": "gone", "m": "old", "same": "x", "y": "bye"}
	b := map[string]string{"b": "fresh", "m": "new", "same": "x", "z": "hi"}
	want := []Change{{"a", "removed", "gone", ""}, {"b", "added", "", "fresh"}, {"m", "changed", "old", "new"}, {"y", "removed", "bye", ""}, {"z", "added", "", "hi"}}
	if got := Diff(a, b); !reflect.DeepEqual(got, want) {
		t.Fatal(got)
	}
	if !reflect.DeepEqual(a, map[string]string{"a": "gone", "m": "old", "same": "x", "y": "bye"}) || !reflect.DeepEqual(b, map[string]string{"b": "fresh", "m": "new", "same": "x", "z": "hi"}) {
		t.Fatal("mutated input", a, b)
	}
}
func TestEmptyValues(t *testing.T) {
	got := Diff(map[string]string{"removed": "", "kept": "", "filled": "", "cleared": "old"}, map[string]string{"added": "", "kept": "", "filled": "new", "cleared": ""})
	want := []Change{{"added", "added", "", ""}, {"cleared", "changed", "old", ""}, {"filled", "changed", "", "new"}, {"removed", "removed", "", ""}}
	if !reflect.DeepEqual(got, want) {
		t.Fatal(got)
	}
}
func TestIdenticalAndNil(t *testing.T) {
	same1, same2 := map[string]string{"a": "b"}, map[string]string{"a": "b"}
	if len(Diff(nil, nil)) != 0 || len(Diff(same1, same2)) != 0 {
		t.Fatal("unchanged emitted")
	}
	if same1["a"] != "b" || same2["a"] != "b" || len(same1) != 1 || len(same2) != 1 {
		t.Fatal("mutated input", same1, same2)
	}
	got := Diff(nil, map[string]string{"x": "y"})
	if len(got) != 1 || got[0].Kind != "added" {
		t.Fatal(got)
	}
}
