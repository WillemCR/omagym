# Workspace switcher

Build a reusable workspace strip using supplied data, without talking to the compositor.

- Main.qml is an Item with workspaces (array of distinct positive integer IDs, initially [1,2,3]), activeId (int, initially 1), and signal requested(int workspaceId).
- Render one Rectangle per ID, in input order, in a horizontal row. Each is named workspace-ID and contains a Text named workspace-label-ID showing the ID, plus a MouseArea named workspace-click-ID.
- The active workspace rectangle is #a6d87b; all others are #344653. Changing activeId updates the colors, including IDs not present in the model (none active).
- Clicking a delegate emits requested with its own ID exactly once. It must not change activeId: the caller owns selection state.
- Replacing workspaces updates the delegates. Nonconsecutive IDs such as [2,7,11] work. An empty array removes all delegates. Do not call Hyprland or any desktop command.

Start in `Main.qml`. The starter loads but deliberately does not meet the requirements. Keep the public properties, signals and object names used by the tests. You may add local QML components.

Run checks from this project folder with `omagym test`, or use **Run tests** in the companion. Omagym restores the canonical `challenge_test.qml` for each run and executes real QML offscreen inside Bubblewrap. Tests inspect live objects, bindings and events. No desktop/session bus, compositor socket or network is available.

For a visual check, run `quickshell --path shell.qml` from this folder. This launches a separate practice window; stop that terminal command with Ctrl+C. It does not install or replace your Omarchy shell configuration. Visual placement on your monitor is a manual check; the automated suite checks component behavior.

## Documentation

- [Repeater](https://doc.qt.io/qt-6/qml-qtquick-repeater.html)
- [Signals and handlers](https://doc.qt.io/qt-6/qtqml-syntax-signals.html)
- [MouseArea](https://doc.qt.io/qt-6/qml-qtquick-mousearea.html)
