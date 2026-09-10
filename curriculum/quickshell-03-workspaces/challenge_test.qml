import QtQuick
import Quickshell

QtObject {
    function test_initial_delegates(s, t) {
        t.waitFor(function(){return t.find(s,"workspace-3") !== null},function(){for(var id=1;id<=3;id++) t.equal(t.find(s,"workspace-label-"+id).text,String(id)); t.ok(t.find(s,"workspace-1").x < t.find(s,"workspace-3").x);});
    }
    function test_active_binding(s, t) {
        t.waitFor(function(){return t.find(s,"workspace-2") !== null},function(){s.activeId=2; t.equal(String(t.find(s,"workspace-2").color),"#a6d87b"); t.equal(String(t.find(s,"workspace-1").color),"#344653"); s.activeId=9; t.equal(String(t.find(s,"workspace-2").color),"#344653");});
    }
    function test_replacement_ids(s, t) {
        s.workspaces=[2,7,11]; t.waitFor(function(){return t.find(s,"workspace-11") !== null},function(){t.equal(t.find(s,"workspace-1"),null); t.equal(t.find(s,"workspace-label-7").text,"7"); t.ok(t.find(s,"workspace-2").x < t.find(s,"workspace-7").x);});
    }
    function test_click_signal(s, t) {
        s.workspaces=[7]; var seen=[]; s.requested.connect(function(id){seen.push(id)}); t.waitFor(function(){return t.find(s,"workspace-click-7") !== null},function(){t.find(s,"workspace-click-7").clicked(null); t.equal(JSON.stringify(seen),"[7]");});
    }
    function test_caller_owns_selection(s, t) {
        t.waitFor(function(){return t.find(s,"workspace-click-2") !== null},function(){t.find(s,"workspace-click-2").clicked(null); t.equal(s.activeId,1);});
    }
    function test_empty_model(s, t) {
        s.workspaces=[]; t.waitFor(function(){return t.find(s,"workspace-1") === null},function(){t.equal(t.find(s,"workspace-2"),null); t.equal(t.find(s,"workspace-3"),null);});
    }
}
