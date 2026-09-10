import QtQuick
import Quickshell

// Owned by Omagym. Runs actual components with a fresh instance per case.
ShellRoot {
    id: root
    property var names: JSON.parse(Quickshell.env("OMAGYM_QML_CHECKS"))
    property int index: -1
    property var suite: null
    property var component: null
    property var subject: null
    property int assertions: 0
    property var predicate: null
    property var continuation: null
    property double deadline: 0

    FloatingWindow {
        id: host
        visible: true
        implicitWidth: 640
        implicitHeight: 240
    }

    QtObject {
        id: checks
        function ok(value, message) {
            root.assertions++
            if (!value) throw new Error(message || "Expected a truthy value")
        }
        function equal(actual, expected, message) {
            root.assertions++
            if (actual !== expected)
                throw new Error((message || "Values differ") + ": expected " + expected + ", received " + actual)
        }
        function find(item, name) {
            if (!item) return null
            if (item.objectName === name) return item
            var children = item.children || []
            for (var i = 0; i < children.length; i++) {
                var found = find(children[i], name)
                if (found) return found
            }
            return null
        }
        function waitFor(condition, then) {
            root.predicate = condition
            root.continuation = then
        }
    }

    function finish(action, detail) {
        poll.stop()
        console.log("OMAGYM_QML_RESULT " + JSON.stringify({name: names[index], action: action, detail: detail || ""}))
        predicate = null
        continuation = null
        if (subject) { subject.destroy(); subject = null }
        next.start()
    }

    function begin() {
        index++
        if (index >= names.length) {
            console.log("OMAGYM_QML_COMPLETE")
            Qt.callLater(Qt.quit)
            return
        }
        assertions = 0
        deadline = Date.now() + 3000
        try {
            subject = component.createObject(host.contentItem)
            if (!subject) throw new Error(component.errorString())
            if (typeof suite[names[index]] !== "function") throw new Error("Named test is missing")
            suite[names[index]](subject, checks)
            if (predicate) poll.start()
            else {
                if (!assertions) throw new Error("Test made no assertions")
                finish("pass", "")
            }
        } catch (error) { finish("fail", String(error)) }
    }

    Timer { id: next; interval: 20; onTriggered: root.begin() }
    Timer {
        id: poll
        interval: 20
        repeat: true
        onTriggered: {
            try {
                if (root.predicate()) {
                    var callback = root.continuation
                    root.predicate = null
                    root.continuation = null
                    callback()
                    if (!root.predicate) {
                        if (!root.assertions) throw new Error("Test made no assertions")
                        root.finish("pass", "")
                    }
                } else if (Date.now() >= root.deadline) throw new Error("Timed out waiting for the required behavior")
            } catch (error) { root.finish("fail", String(error)) }
        }
    }

    Component.onCompleted: {
        var tests = Qt.createComponent(Quickshell.env("OMAGYM_QML_SUITE"))
        component = Qt.createComponent(Quickshell.env("OMAGYM_QML_ENTRY"))
        if (tests.status !== Component.Ready || component.status !== Component.Ready) {
            console.error(tests.errorString() + component.errorString())
            Qt.callLater(Qt.quit)
            return
        }
        suite = tests.createObject(host.contentItem)
        if (!suite) { console.error(tests.errorString()); Qt.callLater(Qt.quit); return }
        next.start()
    }
}
