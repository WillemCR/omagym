package challenge

import "io"

func WriteFrame(w io.Writer, payload []byte) error { return nil }
func ReadFrame(r io.Reader) ([]byte, error)        { return nil, nil }
