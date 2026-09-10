# Language directory

Make a searchable directory with derived results and an honest empty state.

## Your brief

- Display a list named Languages containing Rust, Go, JavaScript and Python in that order. Each list item shows its name and category: Rust and Go are Systems; JavaScript and Python are Scripting.
- Provide Search (text input) and Category (select with All, Systems, Scripting; default All). Match names case-insensitively after trimming the query; combine both filters.
- Show the visible result count in a status named Result count, formatted N results. Show No languages found when empty.
- Provide Clear filters to restore all four entries and reset both controls.

## Work and check

Start in `src/App.jsx`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [React: adding interactivity](https://react.dev/learn/adding-interactivity)
- [React: updating arrays in state](https://react.dev/learn/updating-arrays-in-state)
