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
	var req *http.Request
	next := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		called++
		b, _ := io.ReadAll(r.Body)
		if r != req || r.Method != "POST" || r.URL.String() != "/note?x=1" || string(b) != "hello" || r.Header.Get("Authorization") != "Bearer Zebra-42" || r.Header.Get("X-Trace") != "t1" {
			t.Error("request changed")
		}
		w.Header().Set("X-Note", "yes")
		w.WriteHeader(201)
		w.Write([]byte("saved"))
	})
	req = httptest.NewRequest("POST", "/note?x=1", strings.NewReader("hello"))
	req.Header.Set("Authorization", "Bearer Zebra-42")
	req.Header.Set("X-Trace", "t1")
	w := httptest.NewRecorder()
	RequireToken(next, "Zebra-42").ServeHTTP(w, req)
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
	for _, c := range []struct{ token, header string }{{"", "Bearer "}, {"", "Bearer"}, {"", "Bearer secret"}, {"ok", "Bearer secret"}, {"other", "Bearer ok"}} {
		r := httptest.NewRequest("GET", "/", nil)
		r.Header.Set("Authorization", c.header)
		w := httptest.NewRecorder()
		RequireToken(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { t.Error("wrong token allowed", c) }), c.token).ServeHTTP(w, r)
		if w.Code != 401 {
			t.Fatal(c, w.Code)
		}
	}
}
func TestIndependentHandlers(t *testing.T) {
	ok := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(204) })
	alpha := RequireToken(ok, "alpha")
	beta := RequireToken(ok, "beta")
	for _, c := range []struct {
		h      http.Handler
		header string
		want   int
	}{{alpha, "Bearer beta", 401}, {beta, "Bearer alpha", 401}, {alpha, "Bearer alpha", 204}, {beta, "Bearer beta", 204}} {
		r := httptest.NewRequest("GET", "/", nil)
		r.Header.Set("Authorization", c.header)
		w := httptest.NewRecorder()
		c.h.ServeHTTP(w, r)
		if w.Code != c.want {
			t.Fatal("handlers share configuration", c.header, w.Code, c.want)
		}
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
