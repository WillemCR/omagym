import QtQuick
import Quickshell

QtObject {
    function test_initial_label(s, t) {
        t.equal(t.find(s, "label").text, "CPU: 0%");
    }
    function test_live_text(s, t) {
        s.title = "Memory"; s.percent = 42; t.equal(t.find(s, "label").text, "Memory: 42%");
    }
    function test_clamping(s, t) {
        s.percent = -8; t.equal(t.find(s, "meter").width, 0); t.equal(t.find(s, "label").text, "CPU: 0%"); s.percent = 130; t.equal(t.find(s, "label").text, "CPU: 100%"); t.equal(t.find(s, "meter").width, s.width);
    }
    function test_warning_boundary(s, t) {
        s.percent = 79; t.equal(String(t.find(s,"meter").color), "#a6d87b"); s.percent = 80; t.equal(String(t.find(s,"meter").color), "#ef9a9a");
    }
    function test_threshold_binding(s, t) {
        s.percent = 40; s.warningAt = 40; t.equal(String(t.find(s,"meter").color), "#ef9a9a"); s.warningAt = 41; t.equal(String(t.find(s,"meter").color), "#a6d87b");
    }
    function test_resize_binding(s, t) {
        s.percent = 25; s.width = 400; t.equal(t.find(s,"meter").width, 100); s.width = 200; t.equal(t.find(s,"meter").width, 50);
    }
}
