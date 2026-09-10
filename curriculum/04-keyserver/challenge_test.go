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
	for _, p := range []string{"/", "/kv/", "/kv/x/y", "/other/x"} {
		if w := req(h, "PUT", p, "x"); w.Code != 404 {
			t.Errorf("%s should return 404", p)
		}
	}
	if req(h, "POST", "/kv/x", "").Code != 405 {
		t.Error("unsupported method should return 405")
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
	if req(NewHandler(), "GET", "/kv/x", "").Code != 404 {
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
			key := fmt.Sprintf("/kv/%d", i)
			req(h, "PUT", key, "value")
			if w := req(h, "GET", key, ""); w.Code != 200 || w.Body.String() != "value" {
				t.Errorf("concurrent request failed for %s", key)
			}
		}(i)
	}
	wg.Wait()
}
