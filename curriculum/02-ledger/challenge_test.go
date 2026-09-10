package ledger

import (
	"errors"
	"reflect"
	"strings"
	"testing"
)

func TestTotals(t *testing.T) {
	for _, c := range []struct {
		name, input string
		want        map[string]int
	}{
		{"categories", "category,cents\nfood,250\ntravel,800\nfood,125\n", map[string]int{"food": 375, "travel": 800}},
		{"trim", "category,cents\n food ,0\n", map[string]int{"food": 0}},
		{"quoted", "category,cents\n\"food, drink\",50\n", map[string]int{"food, drink": 50}},
		{"header_only", "category,cents\n", map[string]int{}},
	} {
		t.Run(c.name, func(t *testing.T) {
			got, err := Totals(strings.NewReader(c.input))
			if err != nil || !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, %v; want %v, nil", got, err, c.want)
			}
		})
	}
}
func TestInvalid(t *testing.T) {
	for _, s := range []string{"", "name,cents\nx,1", "category,cents\n,4", "category,cents\nx,-1", "category,cents\nx,1.5", "category,cents\nx", "category,cents\nx,2,3", "category,cents\nx,nope"} {
		t.Run(s, func(t *testing.T) {
			got, err := Totals(strings.NewReader(s))
			if err == nil || got != nil {
				t.Errorf("invalid input should return nil totals and error; got %v, %v", got, err)
			}
		})
	}
}

type brokenReader struct{}

func (brokenReader) Read(p []byte) (int, error) { return 0, errors.New("read failed") }
func TestReaderError(t *testing.T) {
	_, err := Totals(brokenReader{})
	if err == nil {
		t.Error("reader errors must be returned")
	}
}
