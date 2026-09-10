# Wire packets

Read and write length-prefixed messages on a byte stream.

## Your brief

- Implement WriteFrame(w io.Writer,payload []byte) error and ReadFrame(r io.Reader) ([]byte,error).
- A frame is a four-byte unsigned big-endian payload length followed by that many bytes. Payloads may contain any bytes and may be empty. Maximum payload length is 65536 bytes.
- WriteFrame rejects oversized payloads before writing anything, propagates writer errors, and returns io.ErrShortWrite when a Write returns fewer bytes than requested with no error.
- ReadFrame consumes exactly one frame, supports readers returning small chunks, and rejects oversized announced lengths before reading their body.
- Return io.EOF when no header bytes are available and io.ErrUnexpectedEOF for a partial header or body. On error return nil payload. Leave subsequent frames unread.

## Run

Use **Run tests** in Omagym, or `go test -race ./...` in this folder. The starter compiles but intentionally fails behavior checks. Keep the public API; helper files are welcome.

## Documentation

- [Binary encoding](https://pkg.go.dev/encoding/binary)
- [Readers and writers](https://pkg.go.dev/io)
