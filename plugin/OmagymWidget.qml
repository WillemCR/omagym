import QtQuick
import Quickshell

Item {
    id: root
    property QtObject bar: null
    property string moduleName: "willemcr.omagym"
    property var settings: ({})
    readonly property bool vertical: bar ? bar.vertical : false
    implicitWidth: vertical ? (bar ? bar.barSize : 32) : label.implicitWidth + 20
    implicitHeight: bar ? bar.barSize : 32
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: "Open Omagym coding practice"
    Accessible.onPressAction: launch()

    function launch() {
        var script = decodeURIComponent(Qt.resolvedUrl("../scripts/plugin-launch.py").toString().replace(/^file:\/\//, ""))
        Quickshell.execDetached(["xdg-terminal-exec", "--app-id=org.omagym.setup", "-e", "python3", script])
    }

    Keys.onReturnPressed: launch()
    Keys.onSpacePressed: launch()

    Text {
        id: label
        anchors.centerIn: parent
        text: root.vertical ? "<>" : "<> Omagym"
        textFormat: Text.PlainText
        color: root.bar ? root.bar.barForeground : "#cdd6f4"
        font.family: root.bar ? root.bar.fontFamily : "monospace"
        font.pixelSize: 14
        opacity: mouse.containsMouse || root.activeFocus ? 1 : 0.85
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.launch()
        onEntered: if (root.bar) root.bar.showTooltip(root, "Omagym · coding practice\nIndependent project, not supported by DHH or Omacom")
        onExited: if (root.bar) root.bar.hideTooltip(root)
    }
}
