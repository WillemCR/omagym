# Reactive status badge

Build a compact percentage badge that responds to changing data and available space.

- Main.qml is an Item with title (string, initially CPU), percent (int, initially 0), and warningAt (int, initially 80). Its initial width is 240 and height is 40.
- A Text named label displays title followed by a colon, a space, the percentage clamped to 0–100, and %. Changing title or percent must update it immediately.
- A Rectangle named meter has width equal to the component width multiplied by the clamped percentage divided by 100. Resizing the component updates the meter.
- The meter color is #ef9a9a when the clamped percentage is at least warningAt, otherwise #a6d87b. The label must remain readable on the dark practice window.

Start in `Main.qml`. The starter loads but deliberately does not meet the requirements. Keep the public properties, signals and object names used by the tests. You may add local QML components.

Run checks from this project folder with `omagym test`, or use **Run tests** in the companion. Omagym restores the canonical `challenge_test.qml` for each run and executes real QML offscreen inside Bubblewrap. Tests inspect live objects, bindings and events. No desktop/session bus, compositor socket or network is available.

For a visual check, run `quickshell --path shell.qml` from this folder. This launches a separate practice window; stop that terminal command with Ctrl+C. It does not install or replace your Omarchy shell configuration. Visual placement on your monitor is a manual check; the automated suite checks component behavior.

## Documentation

- [Property bindings](https://doc.qt.io/qt-6/qtqml-syntax-propertybinding.html)
- [Rectangle](https://doc.qt.io/qt-6/qml-qtquick-rectangle.html)
