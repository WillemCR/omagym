package challenge

import "testing"

func TestDefaults(t *testing.T) {
	c, e := Parse("# sample\n ")
	if e != nil || c != (Config{"127.0.0.1:8080", 4, false}) {
		t.Fatalf("defaults: %#v %v", c, e)
	}
}
func TestValues(t *testing.T) {
	c, e := Parse(" address = localhost:9000\nworkers=64\ndebug=true")
	if e != nil || c != (Config{"localhost:9000", 64, true}) {
		t.Fatalf("values: %#v %v", c, e)
	}
	c, e = Parse("address=a=b\nworkers=1\ndebug=false")
	if e != nil || c.Address != "a=b" || c.Workers != 1 || c.Debug {
		t.Fatal(c, e)
	}
}
func TestRejectedConfig(t *testing.T) {
	for _, s := range []string{"workers=0", "workers=65", "workers=one", "address= ", "debug=TRUE", "debug=1", "unknown=x", "workers=2\nworkers=3", "bad", "=x"} {
		c, e := Parse(s)
		if e == nil || c != (Config{}) {
			t.Errorf("accepted %q: %#v %v", s, c, e)
		}
	}
}
