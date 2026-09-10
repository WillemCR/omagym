import QtQuick
QtObject {
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
        s.detail="Running"; s.width=500; var label=t.find(s,"detailLabel"); t.equal(label.text,"Running"); t.equal(label.x+label.width,488); s.width=240; t.equal(label.x+label.width,228); t.ok(label.visible);
    }
    function test_reusable_dot(s, t) {
        var dot=t.find(s,"statusDot"); t.equal(dot.width,8); t.equal(dot.height,8); t.equal(dot.radius,4); s.accent="#ef9a9a"; t.equal(String(dot.color),"#ef9a9a");
    }
    function test_spacing_and_vertical_alignment(s, t) {
        s.height=40; var dot=t.find(s,"statusDot"); var label=t.find(s,"panelLabel"); t.equal(dot.x,12); t.equal(dot.y+dot.height/2,20); t.equal(label.x,dot.x+dot.width+8); t.equal(label.y+label.height/2,20);
    }
}
