# Word counter

Build the core of a text analyzer. Turn a string into useful word statistics.

- Implement Analyze(text string) Stats in package wordstats.
- Words are separated by Unicode whitespace. Ignore case when counting unique words; preserve punctuation as part of each word.
- Return Words (total words), Unique (distinct normalized words), and Longest (normalized word with most Unicode characters). Break length ties by first appearance.
- Empty or whitespace-only input returns zero counts and an empty Longest.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
