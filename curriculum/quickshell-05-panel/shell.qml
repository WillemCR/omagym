import QtQuick
import Quickshell

// Launch this separate practice panel manually; the tests exercise Main.qml.
ShellRoot {
    PanelWindow {
        anchors { left: true; right: true; top: true }
        implicitHeight: content.implicitHeight
        color: "#10171e"
        Main { id: content; anchors.fill: parent }
    }
}
