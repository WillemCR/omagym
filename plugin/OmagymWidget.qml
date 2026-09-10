import QtQuick
import Quickshell
import qs.Commons

Item {
    id: root
    property QtObject bar: null
    property string moduleName: "willemcr.omagym"
    property var settings: ({})
    readonly property bool vertical: bar ? bar.vertical : false
    readonly property int barSize: bar ? bar.barSize : Style.bar.sizeHorizontal
    implicitWidth: vertical ? barSize : Style.bar.iconSlot
    implicitHeight: vertical ? Style.bar.iconSlot : barSize
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

    Item {
        id: icon
        anchors.centerIn: parent
        width: 20
        height: 20
        scale: Style.bar.iconCanvas / 20
        rotation: -45
        readonly property color foreground: root.bar ? root.bar.barForeground : "#cdd6f4"
        opacity: mouse.containsMouse || root.activeFocus ? 1 : 0.85

        Rectangle {
            anchors.centerIn: parent
            width: 16
            height: 3
            radius: 1
            color: icon.foreground
        }

        Repeater {
            model: [{ offset: 0, length: 8 }, { offset: 3, length: 14 },
                    { offset: 14, length: 14 }, { offset: 17, length: 8 }]
            Rectangle {
                required property var modelData
                x: modelData.offset
                anchors.verticalCenter: parent.verticalCenter
                width: 3
                height: modelData.length
                radius: 1
                color: icon.foreground
            }
        }
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
