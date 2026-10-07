package keyserver

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
)

func req(h http.Handler, m, p, b string) *httptest.ResponseRecorder {
	w := httptest.NewRecorder()
	h.ServeHTTP(w, httptest.NewRequest(m, p, strings.NewReader(b)))
	return w
}
func TestLifecycle(t *testing.T) {
	h := NewHandler()
	for _, c := range []struct {
		m, p, b string
		code    int
		body    string
	}{{"GET", "/kv/name", "", 404, ""}, {"PUT", "/kv/name", "Willem", 204, ""}, {"GET", "/kv/name", "", 200, "Willem"}, {"PUT", "/kv/name", "Go", 204, ""}, {"GET", "/kv/name", "", 200, "Go"}, {"DELETE", "/kv/name", "", 204, ""}, {"GET", "/kv/name", "", 404, ""}, {"DELETE", "/kv/name", "", 404, ""}} {
		w := req(h, c.m, c.p, c.b)
		if w.Code != c.code {
			t.Errorf("%s %s: status %d, want %d", c.m, c.p, w.Code, c.code)
		}
		if c.code == 200 && w.Body.String() != c.body {
			t.Errorf("body %q; want %q", w.Body.String(), c.body)
		}
	}
}
func TestPathsAndMethods(t *testing.T) {
	h := NewHandler()
	for _, p := range []string{"/", "/kv/", "/kv/x/y", "/kv//x", "/other/x"} {
		if w := req(h, "PUT", p, "x"); w.Code != 404 {
			t.Errorf("%s should return 404", p)
		}
	}
	req(h, "PUT", "/kv/x", "x")
	for _, m := range []string{"POST", "HEAD"} {
		if req(h, m, "/kv/x", "").Code != 405 {
			t.Errorf("%s should return 405", m)
		}
	}
}
func TestIsolationAndEmptyValue(t *testing.T) {
	h := NewHandler()
	if req(h, "PUT", "/kv/x", "").Code != 204 {
		t.Fatal("empty value must be stored")
	}
	if w := req(h, "GET", "/kv/x", ""); w.Code != 200 || w.Body.String() != "" {
		t.Error("empty value must be retrievable")
	}
	req(h, "PUT", "/kv/a", " A\n")
	req(h, "PUT", "/kv/b", "B")
	if w := req(h, "GET", "/kv/a", ""); w.Body.String() != " A\n" {
		t.Errorf("got %q; keys must store their raw body separately", w.Body.String())
	}
	h2 := NewHandler()
	req(h2, "PUT", "/kv/b", "other")
	if req(h2, "GET", "/kv/x", "").Code != 404 || req(h, "GET", "/kv/x", "").Code != 200 || req(h, "GET", "/kv/b", "").Body.String() != "B" {
		t.Error("handlers must not share a store")
	}
}
func TestConcurrent(t *testing.T) {
	h := NewHandler()
	var wg sync.WaitGroup
	for i := 0; i < 30; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key, val := fmt.Sprintf("/kv/%d", i), fmt.Sprint("value", i)
			req(h, "PUT", key, val)
			if w := req(h, "GET", key, ""); w.Code != 200 || w.Body.String() != val {
				t.Errorf("concurrent request failed for %s", key)
			}
			if req(h, "DELETE", key, "").Code != 204 || req(h, "GET", key, "").Code != 404 {
				t.Errorf("concurrent delete failed for %s", key)
			}
		}(i)
	}
	wg.Wait()
}
