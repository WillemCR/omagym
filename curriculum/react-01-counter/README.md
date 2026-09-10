# Rep counter

Build a tiny workout counter with a configurable step and clear bounds.

## Your brief

- Show an output with accessible name Reps, initially 0. Provide buttons Add, Remove and Reset.
- Provide a numeric input labelled Step, initially 1; Add and Remove change the count by that positive integer.
- Never let the count fall below zero; disable Remove at zero. Reset returns the count to zero while preserving Step.
- Blank, zero, negative or non-integer Step values disable Add and Remove until valid again.

## Work and check

Start in `src/App.jsx`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [React: adding interactivity](https://react.dev/learn/adding-interactivity)
- [React: updating arrays in state](https://react.dev/learn/updating-arrays-in-state)
