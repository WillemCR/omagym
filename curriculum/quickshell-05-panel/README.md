# Responsive practice panel

Build responsive panel content from reusable components, then view it in a separate PanelWindow.

- Main.qml is an Item with panelHeight (int, 28), title (string, Omagym practice), detail (string, Ready), accent (color, #a6d87b), and initial width 480. implicitHeight clamps panelHeight to 20–80; height initially follows implicitHeight.
- A Text named panelLabel displays title and is visible only when the component width is at least 320. Changing title and resizing must update it.
- A Text named detailLabel always displays detail. Its right edge stays 12 pixels from the component right edge, including at narrow widths.
- Use a local StatusDot.qml component named statusDot, positioned at x=12. StatusDot is an 8 by 8 circular Rectangle with a dotColor property defaulting to #a6d87b; its rendered color follows dotColor. Main passes accent to the dot.
- Vertically center all three items. panelLabel begins 8 pixels after the dot right edge. Use readable text on the dark practice panel.
- The supplied shell.qml wraps Main in a real top-anchored PanelWindow. Tests exercise the content offscreen; screen-edge placement is a manual check using quickshell --path shell.qml. Ctrl+C closes only this practice panel. Do not modify your installed shell.

Start in `Main.qml` and `StatusDot.qml`. The starter loads but is unsolved. The supplied `shell.qml` is a protected launch wrapper.

Run `omagym test` from this folder or **Run tests** in the companion. The suite inspects live components in an isolated offscreen Quickshell process. It checks binding behavior and item geometry, not source text. No desktop or compositor socket is exposed to tests.

To inspect your work as a real panel, run `quickshell --path shell.qml` and stop it with Ctrl+C. This launches a separate practice panel without replacing or changing the Omarchy configuration. Screen placement is a manual check.

## Documentation

- [PanelWindow](https://quickshell.org/docs/v0.2.1/types/Quickshell/PanelWindow/)
- [Defining QML types](https://doc.qt.io/qt-6/qtqml-documents-definetypes.html)
- [Positioners](https://doc.qt.io/qt-6/qtquick-positioning-layouts.html)
