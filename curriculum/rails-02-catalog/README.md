# Bookshop catalogue scopes

Query a small bookshop catalogue through composable database relations.

- Complete Book < ActiveRecord::Base. The test database has title:string, price_cents:integer, stock:integer, published:boolean.
- Book.available returns an ActiveRecord::Relation containing published books with stock strictly greater than zero, ordered by price_cents ascending then id ascending.
- Book.priced_between(minimum, maximum) returns a relation including both price boundaries. Negative minimum, maximum below minimum, or non-Integer bounds raise ArgumentError.
- Both query methods must compose with each other and with additional where clauses without discarding existing filters. Do not load all books into Ruby arrays.
- Queries must not modify any database records. An empty result remains a relation and supports count and pluck.

Start in `app/models/book.rb`. The gym supplies its project-local Rails, SQLite and Minitest bundle. Tests bootstrap real Rails components with an in-memory database when needed; no separate server is required.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [Active Record querying](https://guides.rubyonrails.org/active_record_querying.html)
- [Active Record basics](https://guides.rubyonrails.org/active_record_basics.html)
