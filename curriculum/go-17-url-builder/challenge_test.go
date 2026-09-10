package challenge

import (
	"reflect"
	"testing"
)

func TestQueryReplacement(t *testing.T) {
	p := map[string][]string{"q": {"go & rust", "vue"}, "page": nil}
	got, e := AddQuery("https://example.com/search?z=last&page=3&q=old#results", p)
	want := "https://example.com/search?q=go+%26+rust&q=vue&z=last#results"
	if e != nil || got != want {
		t.Fatal(got, e)
	}
	if !reflect.DeepEqual(p["q"], []string{"go & rust", "vue"}) || len(p) != 2 {
		t.Fatal("mutated params")
	}
}
func TestQueryBoundaries(t *testing.T) {
	got, e := AddQuery("http://localhost:8080/a%20b?x=", map[string][]string{"empty": {""}})
	if e != nil || got != "http://localhost:8080/a%20b?empty=&x=" {
		t.Fatal(got, e)
	}
	got, e = AddQuery("https://example.com/?a=1", map[string][]string{"a": {}})
	if e != nil || got != "https://example.com/" {
		t.Fatal(got, e)
	}
}
func TestInvalidURLs(t *testing.T) {
	for _, s := range []string{"/relative", "ftp://example.com/a", "https:///path", "https://user:pass@example.com/", "https://example.com/%zz", "https://example.com/?a=%zz", "https://example.com/?a=1;b=2", "https://:8080/"} {
		got, e := AddQuery(s, nil)
		if e == nil || got != "" {
			t.Error(s, got, e)
		}
	}
}
