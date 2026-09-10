# CSV invoice importer

Import supplier invoice lines without floating-point money.

- Implement invoice_totals(io), reading CSV from the supplied IO-like object. The exact header is customer,cents. Return a Hash of customer names to summed Integer cents.
- Trim customer names; preserve case. Cents fields must contain one or more ASCII digits and nothing else (no signs, spaces, decimals or exponents). Leading zeroes are allowed.
- Reject missing/wrong header, malformed CSV, wrong field count, empty names or invalid cents by raising ArgumentError. No partial result may be returned.
- A header-only input returns {}. Quoted names containing commas are valid. Propagate IO read errors unchanged. Do not close the caller-owned IO.

Start in `main.rb`. The gym supplies Minitest from its project-local Ruby bundle. Exercise code uses only Ruby standard libraries.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [CSV](https://ruby.github.io/csv/)
- [IO](https://docs.ruby-lang.org/en/3.4/IO.html)
- [Exceptions](https://docs.ruby-lang.org/en/3.4/Exception.html)
