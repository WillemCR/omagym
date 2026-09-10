package wordstats

import "testing"

func TestAnalyze(t *testing.T) {
	cases := []struct {
		name, input string
		want        Stats
	}{
		{"empty", "", Stats{}},
		{"whitespace", " \t\n", Stats{}},
		{"words", "Go makes Go fun", Stats{4, 3, "makes"}},
		{"case", "GO Go go", Stats{3, 1, "go"}},
		{"tie", "cat dog", Stats{2, 2, "cat"}},
		{"unicode", "éé abc\u2003Go", Stats{3, 3, "abc"}},
		{"punctuation", "Go, go", Stats{2, 2, "go,"}},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := Analyze(c.input); got != c.want {
				t.Errorf("Analyze(%q) = %+v; want %+v", c.input, got, c.want)
			}
		})
	}
}
