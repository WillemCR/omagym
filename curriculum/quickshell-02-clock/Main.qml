import QtQuick
import Quickshell
Item {
    id: root
    width: 240; height: 40
    property bool use24Hours: true
    property bool showSeconds: false
    property var overrideTime: null
    property alias clock: systemClock
    SystemClock { id: systemClock }
    Text { objectName: "clockLabel"; text: "Clock"; color: "white" }
}
