import QtQuick
QtObject {
    // Geometry in panel coordinates, so wrappers are allowed; centring tolerates Qt's whole-pixel alignment.
    function left(s, item) { return item.mapToItem(s, 0, 0).x }
    function right(s, item) { return item.mapToItem(s, item.width, 0).x }
    function centred(s, t, item, name) { var c = item.mapToItem(s, 0, item.height / 2).y; t.ok(Math.abs(c - s.height / 2) <= 1, name + " must be vertically centred, centre at " + c); }
    function centre(s, item) { return item.mapToItem(s, 0, item.height / 2).y }
    // Layouts may apply geometry at the next polish. Wait until the expected geometry appears or stops changing (about 200ms), then assert.
    function settle(t, snapshot, ready, then) {
        var last = null, same = 0;
        t.waitFor(function(){ var now = JSON.stringify(snapshot()); same = now === last ? same + 1 : 0; last = now; return ready() || same >= 10; }, then);
    }
    function test_height_bounds(s, t) {
        s.panelHeight=40; t.equal(s.implicitHeight,40); s.panelHeight=5; t.equal(s.implicitHeight,20); s.panelHeight=200; t.equal(s.implicitHeight,80);
    }
    function test_responsive_title(s, t) {
        s.width=319; t.ok(!t.find(s,"panelLabel").visible,"Hide title below 320px"); s.width=320; t.ok(t.find(s,"panelLabel").visible,"Show title at 320px");
    }
    function test_title_binding(s, t) {
        t.equal(t.find(s,"panelLabel").text,"Omagym practice"); s.title="Focus session"; t.equal(t.find(s,"panelLabel").text,"Focus session");
    }
    function test_detail_binding_and_alignment(s, t) {
        s.detail="Running"; s.width=500; var label=t.find(s,"detailLabel"); t.equal(label.text,"Running");
        var edge=function(){return right(s,label)};
        settle(t,edge,function(){return edge()===488},function(){t.equal(edge(),488); s.width=240;
            settle(t,edge,function(){return edge()===228},function(){t.equal(edge(),228); t.ok(label.visible);});});
    }
    function test_reusable_dot(s, t) {
        var component=Qt.createComponent(Qt.resolvedUrl("StatusDot.qml")); t.equal(component.status,Component.Ready,"StatusDot.qml must load");
        var own=component.createObject(s); t.equal(String(own.dotColor),"#a6d87b"); t.equal(String(own.color),"#a6d87b"); t.equal(own.width,8); t.equal(own.height,8); t.equal(own.radius,4);
        own.dotColor="#90caf9"; t.equal(String(own.color),"#90caf9"); own.destroy();
        var dot=t.find(s,"statusDot"); t.equal(dot.width,8); t.equal(dot.height,8); t.equal(dot.radius,4); s.accent="#ef9a9a"; t.equal(String(dot.dotColor),"#ef9a9a"); t.equal(String(dot.color),"#ef9a9a");
    }
    function test_spacing_and_vertical_alignment(s, t) {
        s.height=40; var dot=t.find(s,"statusDot"); var label=t.find(s,"panelLabel"); var detail=t.find(s,"detailLabel");
        var geometry=function(){return [left(s,dot),right(s,dot),left(s,label),centre(s,dot),centre(s,label),centre(s,detail)]};
        var ok=function(c){return Math.abs(c-20)<=1};
        settle(t,geometry,function(){return left(s,dot)===12 && left(s,label)===right(s,dot)+8 && ok(centre(s,dot)) && ok(centre(s,label)) && ok(centre(s,detail))},
            function(){t.equal(left(s,dot),12); centred(s,t,dot,"statusDot"); t.equal(left(s,label),right(s,dot)+8); centred(s,t,label,"panelLabel"); centred(s,t,detail,"detailLabel");});
    }
}
