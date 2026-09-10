package challenge

import (
	"reflect"
	"testing"
)

func TestMergeBookings(t *testing.T) {
	in := []Interval{{100, 120}, {10, 30}, {25, 60}, {60, 70}, {15, 20}}
	want := []Interval{{10, 70}, {100, 120}}
	out, e := Merge(in)
	if e != nil || !reflect.DeepEqual(out, want) {
		t.Fatalf("got %v %v", out, e)
	}
}
func TestNoMutation(t *testing.T) {
	in := []Interval{{90, 100}, {0, 10}}
	copyIn := append([]Interval(nil), in...)
	out, e := Merge(in)
	if e != nil || len(out) != 2 {
		t.Fatal(out, e)
	}
	if !reflect.DeepEqual(in, copyIn) {
		t.Fatal("input reordered")
	}
	out[0].Start = 99
	if !reflect.DeepEqual(in, copyIn) {
		t.Fatal("result aliases input")
	}
}
func TestBoundaries(t *testing.T) {
	for _, in := range [][]Interval{nil, {}, {{0, 1440}}} {
		out, e := Merge(in)
		if e != nil || len(out) != len(in) {
			t.Fatal(out, e)
		}
	}
	for _, v := range []Interval{{-1, 10}, {0, 1441}, {10, 10}, {12, 4}} {
		out, e := Merge([]Interval{{0, 1}, v})
		if e == nil || out != nil {
			t.Errorf("accepted %v", v)
		}
	}
}
