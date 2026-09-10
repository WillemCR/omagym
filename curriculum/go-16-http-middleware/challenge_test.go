package challenge

import (
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
)

func TestAuthorized(t *testing.T) {
	called := 0
	next := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		called++
		b, _ := io.ReadAll(r.Body)
		if r.Method != "POST" || r.URL.String() != "/note?x=1" || string(b) != "hello" {
			t.Error("request changed")
		}
		w.Header().Set("X-Note", "yes")
		w.WriteHeader(201)
		w.Write([]byte("saved"))
	})
	req := httptest.NewRequest("POST", "/note?x=1", strings.NewReader("hello"))
	req.Header.Set("Authorization", "Bearer secret")
	w := httptest.NewRecorder()
	RequireToken(next, "secret").ServeHTTP(w, req)
	if called != 1 || w.Code != 201 || w.Header().Get("X-Note") != "yes" || w.Body.String() != "saved" {
		t.Fatal(called, w)
	}
}
func TestDenied(t *testing.T) {
	for _, header := range []string{"", "secret", "bearer secret", "Bearer  secret", "Bearer wrong", "Bearer secret "} {
		next := http.HandlerFunc(func(http.ResponseWriter, *http.Request) { t.Error("unauthorized called next") })
		r := httptest.NewRequest("GET", "/", nil)
		r.Header.Set("Authorization", header)
		w := httptest.NewRecorder()
		RequireToken(next, "secret").ServeHTTP(w, r)
		if w.Code != 401 || w.Header().Get("WWW-Authenticate") != "Bearer" || w.Body.String() != "unauthorized\n" {
			t.Fatal(header, w)
		}
	}
	r := httptest.NewRequest("GET", "/", nil)
	r.Header.Set("Authorization", "Bearer ")
	w := httptest.NewRecorder()
	RequireToken(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { t.Error("empty token allowed") }), "").ServeHTTP(w, r)
	if w.Code != 401 {
		t.Fatal(w.Code)
	}
}
func TestConcurrentMiddleware(t *testing.T) {
	h := RequireToken(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(204) }), "ok")
	var wg sync.WaitGroup
	for i := 0; i < 40; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			r := httptest.NewRequest("GET", "/", nil)
			want := 401
			if i%2 == 0 {
				r.Header.Set("Authorization", "Bearer ok")
				want = 204
			}
			w := httptest.NewRecorder()
			h.ServeHTTP(w, r)
			if w.Code != want {
				t.Errorf("got %d want %d", w.Code, want)
			}
		}(i)
	}
	wg.Wait()
}
