# Clock with a testable time source

Make a live clock with predictable formatting and an optional time override.

- Main.qml is an Item with use24Hours (bool, true), showSeconds (bool, false), overrideTime (var, null), and clock, an alias to a real enabled SystemClock.
- A Text named clockLabel shows overrideTime when it is a Date; when overrideTime is null it shows clock.date in local time.
- 24-hour output uses two-digit hours and minutes: 09:05. 12-hour output uses unpadded hours and uppercase AM/PM: 9:05 AM. Midnight is 12:00 AM and noon is 12:00 PM.
- When showSeconds is true, append two-digit seconds before AM/PM if present. Every input property remains reactive.
- Use SystemClock.Minutes precision when seconds are hidden and SystemClock.Seconds when shown. Removing overrideTime returns the display to the live clock.

Start in `Main.qml`. The starter loads but deliberately does not meet the requirements. Keep the public properties, signals and object names used by the tests. You may add local QML components.

Run checks from this project folder with `omagym test`, or use **Run tests** in the companion. Omagym restores the canonical `challenge_test.qml` for each run and executes real QML offscreen inside Bubblewrap. Tests inspect live objects, bindings and events. No desktop/session bus, compositor socket or network is available.

For a visual check, run `quickshell --path shell.qml` from this folder. This launches a separate practice window; stop that terminal command with Ctrl+C. It does not install or replace your Omarchy shell configuration. Visual placement on your monitor is a manual check; the automated suite checks component behavior.

## Documentation

- [SystemClock](https://quickshell.org/docs/v0.2.1/types/Quickshell/SystemClock/)
- [Qt date formatting](https://doc.qt.io/qt-6/qml-qtqml-qt.html#formatDateTime-method)
