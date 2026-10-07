package challenge

import (
	"bytes"
	"encoding/binary"
	"errors"
	"io"
	"testing"
)

func TestFrameRoundTrip(t *testing.T) {
	var b bytes.Buffer
	for _, p := range [][]byte{[]byte("hello"), {}, {0, 255, 10}, make([]byte, 65536)} {
		if e := WriteFrame(&b, p); e != nil {
			t.Fatal(e)
		}
	}
	for _, want := range [][]byte{[]byte("hello"), {}, {0, 255, 10}, make([]byte, 65536)} {
		got, e := ReadFrame(&b)
		if e != nil || !bytes.Equal(got, want) {
			t.Fatal(len(got), e)
		}
	}
	if _, e := ReadFrame(&b); !errors.Is(e, io.EOF) {
		t.Fatal(e)
	}
}
func TestWireFormatAndChunks(t *testing.T) {
	var b bytes.Buffer
	WriteFrame(&b, []byte("ab"))
	if !bytes.Equal(b.Bytes(), []byte{0, 0, 0, 2, 'a', 'b'}) {
		t.Fatal(b.Bytes())
	}
	p, e := ReadFrame(oneByte{bytes.NewReader([]byte{0, 0, 0, 2, 'a', 'b', 99})})
	if e != nil || string(p) != "ab" {
		t.Fatal(p, e)
	}
}

type oneByte struct{ io.Reader }

func (r oneByte) Read(p []byte) (int, error) {
	if len(p) > 1 {
		p = p[:1]
	}
	return r.Reader.Read(p)
}
func TestMalformedFrames(t *testing.T) {
	for _, v := range [][]byte{{0}, {0, 0, 0}, {0, 0, 0, 2}, {0, 0, 0, 2, 'a'}} {
		p, e := ReadFrame(bytes.NewReader(v))
		if p != nil || !errors.Is(e, io.ErrUnexpectedEOF) {
			t.Fatal(v, p, e)
		}
	}
	var h [4]byte
	binary.BigEndian.PutUint32(h[:], 65537)
	for _, n := range []uint32{65537, 1 << 31, 1<<32 - 1} {
		binary.BigEndian.PutUint32(h[:], n)
		body := &trapReader{}
		if p, e := ReadFrame(io.MultiReader(bytes.NewReader(h[:]), body)); e == nil || p != nil || body.reads != 0 {
			t.Fatal("oversize frame accepted or body read", n, len(p), e, body.reads)
		}
	}
	var b bytes.Buffer
	if e := WriteFrame(&b, make([]byte, 65537)); e == nil || b.Len() != 0 {
		t.Fatal("oversize write")
	}
}

// trapReader stands in for an oversized body: it counts read attempts and supplies up to 1 MiB.
type trapReader struct{ reads, sent int }

func (r *trapReader) Read(p []byte) (int, error) {
	r.reads++
	if r.sent >= 1<<20 {
		return 0, io.EOF
	}
	n := min(len(p), 1<<20-r.sent)
	r.sent += n
	return n, nil
}

// limitWriter accepts the first limit bytes, then reports err (nil means a silent short write).
type limitWriter struct {
	limit int
	err   error
	buf   []byte
}

func (w *limitWriter) Write(p []byte) (int, error) {
	n := min(len(p), w.limit-len(w.buf))
	w.buf = append(w.buf, p[:n]...)
	if n < len(p) {
		return n, w.err
	}
	return n, nil
}

// fullErrWriter accepts every byte but reports err once byte offset at has been written.
type fullErrWriter struct {
	at, n int
	err   error
}

func (w *fullErrWriter) Write(p []byte) (int, error) {
	w.n += len(p)
	if w.n > w.at {
		return len(p), w.err
	}
	return len(p), nil
}

type shortWriter struct{}

func (shortWriter) Write(p []byte) (int, error) { return 0, nil }

type errorWriter struct{ err error }

func (w errorWriter) Write(p []byte) (int, error) { return 0, w.err }
func TestWriterFailure(t *testing.T) {
	if e := WriteFrame(shortWriter{}, []byte("x")); !errors.Is(e, io.ErrShortWrite) {
		t.Fatal(e)
	}
	sentinel := errors.New("write failed")
	if e := WriteFrame(errorWriter{sentinel}, nil); !errors.Is(e, sentinel) {
		t.Fatal(e)
	}
	for _, limit := range []int{4, 5} {
		if e := WriteFrame(&limitWriter{limit: limit, err: sentinel}, []byte("xyz")); !errors.Is(e, sentinel) {
			t.Fatal("payload write error ignored", limit, e)
		}
		if e := WriteFrame(&limitWriter{limit: limit}, []byte("xyz")); !errors.Is(e, io.ErrShortWrite) {
			t.Fatal("short payload write ignored", limit, e)
		}
	}
	for _, at := range []int{0, 4} {
		if e := WriteFrame(&fullErrWriter{at: at, err: sentinel}, []byte("xyz")); !errors.Is(e, sentinel) {
			t.Fatal("error returned with a full byte count was ignored", at, e)
		}
	}
}
