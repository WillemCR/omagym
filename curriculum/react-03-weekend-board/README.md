# Weekend board

Turn a blank board into a useful, persistent weekend checklist.

## Your brief

- Provide a Task input and Add task button. Trim submissions, reject blank text, append a task and clear the input. Start empty when storage is empty.
- Each task is a list item in a list named Tasks, with a checkbox labelled by its task text and a Delete <task text> button. Duplicate text is allowed; task identities remain independent.
- Show a status named Remaining with N remaining. Checkbox toggles update the count; deleting removes only the chosen task.
- Persist tasks and completion under localStorage key omagym-weekend-tasks so reload restores them. A malformed value at that key must recover to an empty usable board.

## Work and check

Start in `src/App.jsx`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [React: adding interactivity](https://react.dev/learn/adding-interactivity)
- [React: updating arrays in state](https://react.dev/learn/updating-arrays-in-state)
- [React: synchronizing with effects](https://react.dev/learn/synchronizing-with-effects)
