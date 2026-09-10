package challenge

import (
	"reflect"
	"testing"
)

func TestChanges(t *testing.T) {
	a := map[string]string{"z": "old", "b": "gone", "same": "x"}
	b := map[string]string{"z": "new", "a": "fresh", "same": "x"}
	want := []Change{{"a", "added", "", "fresh"}, {"b", "removed", "gone", ""}, {"z", "changed", "old", "new"}}
	if got := Diff(a, b); !reflect.DeepEqual(got, want) {
		t.Fatal(got)
	}
	if a["z"] != "old" || len(a) != 3 || b["z"] != "new" || len(b) != 3 {
		t.Fatal("mutated input")
	}
}
func TestEmptyValues(t *testing.T) {
	got := Diff(map[string]string{"removed": "", "kept": ""}, map[string]string{"added": "", "kept": ""})
	want := []Change{{"added", "added", "", ""}, {"removed", "removed", "", ""}}
	if !reflect.DeepEqual(got, want) {
		t.Fatal(got)
	}
}
func TestIdenticalAndNil(t *testing.T) {
	if len(Diff(nil, nil)) != 0 || len(Diff(map[string]string{"a": "b"}, map[string]string{"a": "b"})) != 0 {
		t.Fatal("unchanged emitted")
	}
	got := Diff(nil, map[string]string{"x": "y"})
	if len(got) != 1 || got[0].Kind != "added" {
		t.Fatal(got)
	}
}
