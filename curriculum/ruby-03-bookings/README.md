# Room booking calendar

Manage room bookings with conflict detection and safe cancellation.

- Implement BookingCalendar with book(id:, room:, start_at:, end_at:), cancel(id), and bookings(room). IDs and room names are non-empty Strings with no edge whitespace; times are Integers and start_at must be less than end_at.
- book returns true on success. Duplicate IDs across all rooms, invalid arguments, or overlap in the same room raise ArgumentError and leave state unchanged.
- Intervals are half-open: one booking ending exactly when another starts does not overlap. Different rooms can overlap.
- cancel returns true when an ID existed and false otherwise. bookings(room) returns hashes with :id, :room, :start_at, :end_at, sorted by start_at then id. Unknown rooms return [].
- All values passed into book and all returned hashes/strings must be isolated from internal state: caller mutations must not change saved bookings. Independent calendars must not share state.

Start in `main.rb`. The gym supplies Minitest from its project-local Ruby bundle. Exercise code uses only Ruby standard libraries.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [Classes](https://docs.ruby-lang.org/en/3.4/syntax/modules_and_classes_rdoc.html)
- [Array](https://docs.ruby-lang.org/en/3.4/Array.html)
- [Object copying](https://docs.ruby-lang.org/en/3.4/Object.html)
