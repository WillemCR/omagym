import QtQuick
import Quickshell
import QtTest

QtObject {
    // Real pointer input delivered through the window, so hit testing and MouseEvent apply.
    property var pointer: TestEvent {}
    function click(t, item) {
        t.ok(item.visible && item.enabled && item.width > 0 && item.height > 0, "Click area must be visible, enabled and sized");
        t.ok(pointer.mouseClick(item, item.width / 2, item.height / 2, Qt.LeftButton, Qt.NoModifier, -1), "Window not shown");
    }
    function test_initial_delegates(s, t) {
        t.waitFor(function(){return t.find(s,"workspace-3") !== null},function(){for(var id=1;id<=3;id++) t.equal(t.find(s,"workspace-label-"+id).text,String(id)); t.ok(t.find(s,"workspace-1").mapToItem(s,0,0).x < t.find(s,"workspace-3").mapToItem(s,0,0).x);});
    }
    function test_active_binding(s, t) {
        t.waitFor(function(){return t.find(s,"workspace-2") !== null},function(){s.activeId=2; t.equal(String(t.find(s,"workspace-2").color),"#a6d87b"); t.equal(String(t.find(s,"workspace-1").color),"#344653"); s.activeId=9; t.equal(String(t.find(s,"workspace-2").color),"#344653");});
    }
    function test_replacement_ids(s, t) {
        s.workspaces=[11,2,7]; t.waitFor(function(){return t.find(s,"workspace-11") !== null},function(){t.equal(t.find(s,"workspace-1"),null); t.equal(t.find(s,"workspace-label-7").text,"7"); var x=function(id){return t.find(s,"workspace-"+id).mapToItem(s,0,0).x}; t.ok(x(11) < x(2) && x(2) < x(7), "Delegates must follow input order");});
    }
    function test_click_signal(s, t) {
        s.workspaces=[7]; var seen=[]; s.requested.connect(function(id){seen.push(id)}); t.waitFor(function(){return t.find(s,"workspace-click-7") !== null},function(){click(t,t.find(s,"workspace-7")); t.equal(JSON.stringify(seen),"[7]");});
    }
    function test_caller_owns_selection(s, t) {
        var seen=[]; s.requested.connect(function(id){seen.push(id)}); t.waitFor(function(){return t.find(s,"workspace-click-2") !== null},function(){click(t,t.find(s,"workspace-2")); t.equal(JSON.stringify(seen),"[2]"); t.equal(s.activeId,1);});
    }
    function test_empty_model(s, t) {
        s.workspaces=[]; t.waitFor(function(){return t.find(s,"workspace-1") === null},function(){t.equal(t.find(s,"workspace-2"),null); t.equal(t.find(s,"workspace-3"),null);});
    }
}
