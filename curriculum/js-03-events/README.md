# Snapshot event bus

Build the event layer behind a tiny interactive application.

- Export createEventBus(), returning an object with on(event, listener), emit(event, payload), and listenerCount(event). Event names are strings and listeners are functions; reject invalid arguments with TypeError.
- on returns an idempotent unsubscribe function. Each registration is independent, even when the same function is registered twice. listenerCount reports active registrations for that event.
- emit calls listeners synchronously in registration order with the exact payload reference and returns the number called. No listeners returns zero.
- Each emit takes a snapshot of registrations at its start. Changes made by a callback apply to later emits; removing a listener during dispatch does not skip it in the current snapshot.
- Nested emits take a fresh snapshot of current registrations. If a listener throws, propagate the exact error and stop that emit; leave registrations intact. Separate bus instances must be isolated. Event names such as __proto__ are valid.

Start in `main.js`. Keep public signatures and types. The starter deliberately has no implementation.

Run `node --test --test-reporter=spec` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
- [Set](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)
- [Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
