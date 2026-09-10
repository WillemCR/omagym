import QtQuick
Item {
    id: root
    width: 240; height: 40
    property string title: "CPU"
    property int percent: 0
    property int warningAt: 80
    Rectangle { objectName: "meter"; anchors.bottom: parent.bottom; width: 0; height: 4; color: "#888888" }
    Text { objectName: "label"; text: "Status badge"; color: "white" }
}
