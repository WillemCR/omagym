package taskstore

import (
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

func TestRoundTrip(t *testing.T) {
	p := filepath.Join(t.TempDir(), "tasks.json")
	want := []Task{{1, "Learn Go", false}, {2, "Write tests", true}}
	if err := Save(p, want); err != nil {
		t.Fatal(err)
	}
	got, err := Load(p)
	if err != nil || !reflect.DeepEqual(got, want) {
		t.Fatalf("round trip got %v, %v; want %v", got, err, want)
	}
	b, _ := os.ReadFile(p)
	if !strings.Contains(string(b), `"title"`) {
		t.Error("use lowercase JSON keys")
	}
}
func TestMissing(t *testing.T) {
	got, err := Load(filepath.Join(t.TempDir(), "missing"))
	if err != nil || len(got) != 0 {
		t.Errorf("missing file got %v %v", got, err)
	}
}
func TestEmpty(t *testing.T) {
	p := filepath.Join(t.TempDir(), "tasks.json")
	if err := Save(p, nil); err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(p)
	if err != nil || strings.TrimSpace(string(b)) != "[]" {
		t.Errorf("empty tasks should be []; got %q %v", b, err)
	}
}
func TestInvalidTasks(t *testing.T) {
	for _, tasks := range [][]Task{{{0, "x", false}}, {{1, " \t", false}}, {{1, "x", false}, {1, "y", true}}} {
		p := filepath.Join(t.TempDir(), "tasks.json")
		os.WriteFile(p, []byte("[]"), 0600)
		if Save(p, tasks) == nil {
			t.Error("invalid tasks accepted")
		}
		b, _ := os.ReadFile(p)
		if string(b) != "[]" {
			t.Error("invalid input changed file")
		}
	}
}
func TestInvalidFiles(t *testing.T) {
	for _, s := range []string{`{`, `[] []`, `[{"id":0,"title":"x"}]`, `[{"id":1,"title":" "}]`, `[{"id":1,"title":"x"},{"id":1,"title":"y"}]`} {
		p := filepath.Join(t.TempDir(), "tasks.json")
		os.WriteFile(p, []byte(s), 0600)
		if _, err := Load(p); err == nil {
			t.Errorf("accepted invalid data %q", s)
		}
	}
}
func TestIOErrors(t *testing.T) {
	dir := t.TempDir()
	if Save(dir, []Task{{1, "x", false}}) == nil {
		t.Error("save to directory should fail")
	}
	if _, err := Load(dir); err == nil {
		t.Error("load directory should fail")
	}
}
