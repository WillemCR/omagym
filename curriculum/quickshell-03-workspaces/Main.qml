import QtQuick
Item {
    id: root
    width: 260; height: 36
    property var workspaces: [1, 2, 3]
    property int activeId: 1
    signal requested(int workspaceId)
    Row { spacing: 6; Text { text: "Workspaces"; color: "white" } }
}
