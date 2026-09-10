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
	if p, e := ReadFrame(bytes.NewReader(h[:])); e == nil || p != nil {
		t.Fatal("oversize")
	}
	var b bytes.Buffer
	if e := WriteFrame(&b, make([]byte, 65537)); e == nil || b.Len() != 0 {
		t.Fatal("oversize write")
	}
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
}
