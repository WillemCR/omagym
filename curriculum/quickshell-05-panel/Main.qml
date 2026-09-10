import QtQuick
Item {
    id: root
    width: 480
    height: implicitHeight
    property int panelHeight: 28
    property string title: "Omagym practice"
    property string detail: "Ready"
    property color accent: "#a6d87b"
    implicitHeight: 20
    Text { objectName: "panelLabel"; text: "Practice panel"; color: "white" }
    Text { objectName: "detailLabel"; text: ""; color: "white"; x: 250 }
    StatusDot { objectName: "statusDot"; x: 200 }
}
