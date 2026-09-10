package challenge

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"io/fs"
	"testing"
	"testing/fstest"
)

func TestManifest(t *testing.T) {
	f := fstest.MapFS{"z.txt": {Data: []byte("abc")}, "dir/empty": {Data: []byte{}}, ".hidden": {Data: []byte("x")}}
	got, e := Manifest(f)
	if e != nil || len(got) != 3 {
		t.Fatal(got, e)
	}
	paths := []string{".hidden", "dir/empty", "z.txt"}
	for i, p := range paths {
		want := fmt.Sprintf("%x", sha256.Sum256(f[p].Data))
		if got[i].Path != p || got[i].Size != int64(len(f[p].Data)) || got[i].SHA256 != want {
			t.Fatal(got[i])
		}
	}
}
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
	got, e = Manifest(fstest.MapFS{"link": {Mode: fs.ModeSymlink, Data: []byte("target")}})
	if got != nil || e == nil {
		t.Fatal("symlink accepted", got, e)
	}
	got, e = Manifest(readFailureFS{fstest.MapFS{"unreadable": {Data: []byte("data")}}})
	if got != nil || !errors.Is(e, fs.ErrPermission) {
		t.Fatal("read error was not propagated", got, e)
	}
}
