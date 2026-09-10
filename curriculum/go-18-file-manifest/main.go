package challenge

import "io/fs"

type Entry struct {
	Path   string
	Size   int64
	SHA256 string
}

func Manifest(fsys fs.FS) ([]Entry, error) { return nil, nil }
