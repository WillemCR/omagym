import QtQuick
import Quickshell.Io
Item {
    id: root
    width: 360; height: 60
    property var command: ["/usr/bin/printf", "%s\n", "ready"]
    property string status: "idle"
    property string output: ""
    property alias job: process
    function refresh() { /* Implement the refresh lifecycle. */ }
    Process { id: process; command: root.command }
    Column {
        Text { objectName: "statusLabel"; text: "idle"; color: "white" }
        Text { objectName: "outputLabel"; text: ""; color: "white" }
    }
}
