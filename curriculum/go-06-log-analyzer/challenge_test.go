package challenge

import (
	"errors"
	"io"
	"reflect"
	"strings"
	"testing"
)

func TestSummary(t *testing.T) {
	r, e := Analyze(strings.NewReader(" INFO | ready\nERROR|first\nWARN|a|b\nERROR | last|retry \n"))
	if e != nil || !reflect.DeepEqual(r.Counts, map[string]int{"INFO": 1, "WARN": 1, "ERROR": 2}) || r.LastError != "last|retry" {
		t.Fatalf("unexpected report: %#v %v", r, e)
	}
}
func TestEmpty(t *testing.T) {
	r, e := Analyze(strings.NewReader(" \n\t"))
	if e != nil || r.Counts == nil || len(r.Counts) != 0 || r.LastError != "" {
		t.Fatalf("empty: %#v %v", r, e)
	}
}
func TestMalformed(t *testing.T) {
	for _, s := range []string{"DEBUG|x", "INFO| ", "INFO x", "INFO|ok\nnope"} {
		r, e := Analyze(strings.NewReader(s))
		if e == nil || r.Counts != nil {
			t.Errorf("accepted %q: %#v %v", s, r, e)
		}
	}
}

var errDisk = errors.New("disk unavailable")

type brokenReader struct{}

func (brokenReader) Read([]byte) (int, error) { return 0, errDisk }
func TestReaderFailure(t *testing.T) {
	for _, in := range []io.Reader{brokenReader{}, io.MultiReader(strings.NewReader("INFO|ok\nERROR|x\n"), brokenReader{})} {
		r, e := Analyze(in)
		if !errors.Is(e, errDisk) || r.Counts != nil {
			t.Fatalf("must propagate reader failure with nil Counts: %#v %v", r, e)
		}
	}
}
