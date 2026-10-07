package challenge

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"reflect"
	"testing"
	"testing/fstest"
)

func TestManifest(t *testing.T) {
	f := fstest.MapFS{"z.txt": {Data: []byte("abc")}, "dir/empty": {Data: []byte{}}, ".hidden": {Data: []byte("x")}, "a/z": {Data: []byte("nested")}, "a.txt": {Data: []byte("flat")}}
	got, e := Manifest(f)
	paths := []string{".hidden", "a.txt", "a/z", "dir/empty", "z.txt"}
	if e != nil || len(got) != len(paths) {
		t.Fatal(got, e)
	}
	for i, p := range paths {
		want := fmt.Sprintf("%x", sha256.Sum256(f[p].Data))
		if got[i].Path != p || got[i].Size != int64(len(f[p].Data)) || got[i].SHA256 != want {
			t.Fatal(got[i])
		}
	}
	got, e = Manifest(truncatedFS{fstest.MapFS{"long": {Data: []byte("abcdefgh")}}})
	wantShort := []Entry{{"long", 3, fmt.Sprintf("%x", sha256.Sum256([]byte("abc")))}}
	if e != nil || !reflect.DeepEqual(got, wantShort) {
		t.Fatal("size or digest not based on bytes read", got, e)
	}
}

// truncatedFS serves only the first 3 bytes of each top-level file while metadata reports the full size.
type truncatedFS struct{ fs.FS }
type truncatedFile struct {
	fs.File
	r io.Reader
}

func (f truncatedFS) Open(name string) (fs.File, error) {
	file, err := f.FS.Open(name)
	if err != nil || name == "." {
		return file, err
	}
	return truncatedFile{file, io.LimitReader(file, 3)}, nil
}
func (f truncatedFile) Read(p []byte) (int, error) { return f.r.Read(p) }

func TestEmptyManifest(t *testing.T) {
	got, e := Manifest(fstest.MapFS{})
	if e != nil || len(got) != 0 {
		t.Fatal(got, e)
	}
}

type failedFS struct{}

func (failedFS) Open(string) (fs.File, error) { return nil, fs.ErrPermission }

type readFailureFS struct{ fs.FS }
type readFailureFile struct{ fs.File }

func (f readFailureFS) Open(name string) (fs.File, error) {
	file, err := f.FS.Open(name)
	if err != nil || name == "." {
		return file, err
	}
	return readFailureFile{file}, nil
}
func (f readFailureFile) Read([]byte) (int, error) { return 0, fs.ErrPermission }

func TestManifestErrors(t *testing.T) {
	got, e := Manifest(failedFS{})
	if got != nil || !errors.Is(e, fs.ErrPermission) {
		t.Fatal(got, e)
	}
	for _, mode := range []fs.FileMode{fs.ModeSymlink, fs.ModeNamedPipe, fs.ModeDevice} {
		got, e = Manifest(fstest.MapFS{"a-good": {Data: []byte("ok")}, "z-special": {Mode: mode, Data: []byte("target")}})
		if got != nil || e == nil {
			t.Fatal("non-regular entry accepted or partial result returned", mode, got, e)
		}
	}
	got, e = Manifest(readFailureFS{fstest.MapFS{"unreadable": {Data: []byte("data")}}})
	if got != nil || !errors.Is(e, fs.ErrPermission) {
		t.Fatal("read error was not propagated", got, e)
	}
}
