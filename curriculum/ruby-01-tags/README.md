# Reading-list tag index

Turn article tags into a reusable browsing index.

- Implement tag_index(articles). Input is an Array of Hashes with symbol keys :id and :tags. IDs are unique positive Integers; tags is an Array of Strings. Invalid input raises ArgumentError.
- Trim and lowercase each tag. Ignore blank tags. Within one article count a normalized tag only once.
- Return a Hash mapping each normalized tag to its article IDs sorted ascending. A tag may include punctuation or Unicode; use Ruby downcase.
- Empty input returns {}. Do not mutate the input hashes, arrays or strings.

Start in `main.rb`. The gym supplies Minitest from its project-local Ruby bundle. Exercise code uses only Ruby standard libraries.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [Enumerable](https://docs.ruby-lang.org/en/3.4/Enumerable.html)
- [Hash](https://docs.ruby-lang.org/en/3.4/Hash.html)
- [String](https://docs.ruby-lang.org/en/3.4/String.html)
