package challenge

import (
	"reflect"
	"testing"
)

func TestBuildOrder(t *testing.T) {
	g := map[string][]string{"app": {"lib", "test"}, "lib": {"base", "base"}, "test": {"base"}, "base": {}, "aaa": {}}
	got, e := Order(g)
	want := []string{"aaa", "base", "lib", "test", "app"}
	if e != nil || !reflect.DeepEqual(got, want) {
		t.Fatal(got, e)
	}
	if !reflect.DeepEqual(g["lib"], []string{"base", "base"}) {
		t.Fatal("mutated dependencies")
	}
}
func TestReadySelection(t *testing.T) {
	g := map[string][]string{"z": {}, "b": {"a"}, "a": {}}
	for i := 0; i < 20; i++ {
		v, e := Order(g)
		if e != nil || !reflect.DeepEqual(v, []string{"a", "b", "z"}) {
			t.Fatal(v, e)
		}
	}
}
func TestInvalidGraph(t *testing.T) {
	for _, g := range []map[string][]string{{"a": {"missing"}}, {"a": {"b"}, "b": {"a"}}, {"a": {"a"}}, {"": {}}, {"ok": {}, "a": {"a"}}} {
		v, e := Order(g)
		if e == nil || v != nil {
			t.Fatal("accepted graph", g, v, e)
		}
	}
	v, e := Order(nil)
	if e != nil || len(v) != 0 {
		t.Fatal(v, e)
	}
}
