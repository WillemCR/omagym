package challenge

import "io"

type Report struct {
	Counts    map[string]int
	LastError string
}

func Analyze(r io.Reader) (Report, error) { return Report{}, nil }
