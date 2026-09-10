# Folder manifest

Produce a portable fingerprint manifest for every file in a virtual filesystem.

## Your brief

- Implement Manifest(fsys fs.FS) ([]Entry,error). Entry has Path string, Size int64, SHA256 string.
- Walk from . and include every regular file, including dotfiles, recursively. Exclude directories. Return entries sorted lexicographically by slash-separated Path.
- Size is the number of bytes read and SHA256 is the lowercase hexadecimal SHA-256 digest of those bytes. Empty files are included.
- Reject non-regular entries such as symlinks rather than following them. Propagate walk, open and read errors; on any error return nil entries.
- Use only the supplied fs.FS, never the host working directory. Empty filesystems succeed with an empty result.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Filesystem interfaces](https://pkg.go.dev/io/fs)
- [SHA-256](https://pkg.go.dev/crypto/sha256)
