# Command status widget

Display the result of a bounded local command and handle failure and refresh safely.

- Main.qml is an Item with command (argument array, initially [/usr/bin/printf, %s\n, ready]), status (string, idle), output (string, empty), alias job for its Quickshell.Io Process, and function refresh(). Do not auto-run on creation.
- refresh starts command using Process argument arrays, sets status to running and clears output. Never wrap the command in a shell; spaces, semicolons and dollar signs are literal arguments.
- Collect stdout with StdioCollector and store its trimmed text in output when finished. On exit code 0 set status to success; on any nonzero exit code set error. Empty output is valid.
- Calling refresh while the process is running must be ignored, without restarting it. After completion, changing command and calling refresh starts a new run, including recovery from error.
- A Text named statusLabel displays status and a Text named outputLabel displays output, both reactively. Tests use only printf, false and a short sleep in the sandbox; do not add commands that alter the system.

Start in `Main.qml`. The starter loads but deliberately does not meet the requirements. Keep the public properties, signals and object names used by the tests. You may add local QML components.

Run checks from this project folder with `omagym test`, or use **Run tests** in the companion. Omagym restores the canonical `challenge_test.qml` for each run and executes real QML offscreen inside Bubblewrap. Tests inspect live objects, bindings and events. No desktop/session bus, compositor socket or network is available.

For a visual check, run `quickshell --path shell.qml` from this folder. This launches a separate practice window; stop that terminal command with Ctrl+C. It does not install or replace your Omarchy shell configuration. Visual placement on your monitor is a manual check; the automated suite checks component behavior.

## Documentation

- [Process](https://quickshell.org/docs/v0.2.1/types/Quickshell.Io/Process/)
- [StdioCollector](https://quickshell.org/docs/v0.2.1/types/Quickshell.Io/StdioCollector/)
