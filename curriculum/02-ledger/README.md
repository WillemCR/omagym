# Expense ledger

Read expense records and report how much was spent in each category.

- Implement Totals(r io.Reader) (map[string]int, error) in package ledger.
- Input is CSV with the exact header category,cents. Trim category whitespace. Cents must be a non-negative base-10 integer.
- Sum cents per category. Empty categories, wrong headers, missing fields, non-integers and negative amounts return an error and nil totals.
- A header-only file returns an empty map and no error. Propagate reader errors. No floating-point currency.

Run `go test -v ./...` in this folder. The gym runs a fresh copy of the original tests.
